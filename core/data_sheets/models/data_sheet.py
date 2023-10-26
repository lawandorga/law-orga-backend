import json
from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID, uuid4

from django.core.files.base import File as DjangoFile
from django.db import models
from django.utils.timezone import localtime

from core.auth.models import RlcUser
from core.data_sheets.models.encrypted_client import EncryptedClient  # type: ignore
from core.data_sheets.models.template import (
    DataSheetEncryptedFileField,
    DataSheetEncryptedSelectField,
    DataSheetEncryptedStandardField,
    DataSheetMultipleField,
    DataSheetSelectField,
    DataSheetStandardField,
    DataSheetStateField,
    DataSheetStatisticField,
    DataSheetTemplate,
    DataSheetUsersField,
)
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.folder_addon import FolderAddon
from core.permissions.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from core.seedwork.aggregate import Aggregate
from core.seedwork.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption
from core.seedwork.events_addon import EventsAddon


###
# Record
###
class DjangoRecordRepository(ItemRepository):
    IDENTIFIER = "RECORD"

    @classmethod
    def retrieve(cls, uuid: UUID, org_pk: Optional[int] = None) -> "DataSheet":
        assert isinstance(uuid, UUID)
        return DataSheet.objects.get(uuid=uuid)


class DataSheet(Aggregate, models.Model):
    REPOSITORY = DjangoRecordRepository.IDENTIFIER

    @classmethod
    def create(
        cls,
        user: RlcUser,
        folder: Folder,
        template: DataSheetTemplate,
        name: str,
        users: list[RlcUser] | None = None,
        pk=0,
    ) -> "DataSheet":
        if users is None:
            users = []

        for u in users:
            if u.has_permission(
                PERMISSION_RECORDS_ACCESS_ALL_RECORDS
            ) and not folder.has_access(user):
                folder.grant_access(u, user)

        record = DataSheet(template=template, name=name)
        record.set_folder(folder)
        record.generate_key(user)

        if pk:
            record.pk = pk

        return record

    template = models.ForeignKey(
        DataSheetTemplate, related_name="records", on_delete=models.PROTECT
    )
    folder_uuid = models.UUIDField(db_index=True, null=True)
    uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)
    old_client = models.ForeignKey(
        EncryptedClient,
        related_name="records",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=300, default="-")
    key = models.JSONField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    addons = {"events": EventsAddon, "folder": FolderAddon}
    events: EventsAddon
    folder: FolderAddon

    UNENCRYPTED_ENTRY_TYPES = [
        "state_entries",
        "statistic_entries",
        "multiple_entries",
        "standard_entries",
        "select_entries",
        "users_entries",
    ]

    ENCRYPTED_ENTRY_TYPES = [
        "encrypted_select_entries",
        "encrypted_file_entries",
        "encrypted_standard_entries",
    ]

    UNENCRYPTED_PREFETCH_RELATED = [
        "state_entries",
        "state_entries__field",
        "select_entries",
        "select_entries__field",
        "standard_entries",
        "standard_entries__field",
        "users_entries",
        "users_entries__value",
        "users_entries__field",
        "multiple_entries",
        "multiple_entries__field",
        "encryptions",
    ]

    ALL_PREFETCH_RELATED = [
        "encrypted_select_entries",
        "encrypted_select_entries__field",
        "encrypted_standard_entries",
        "encrypted_standard_entries__field",
        "encrypted_file_entries",
        "encrypted_file_entries__field",
        "statistic_entries",
        "statistic_entries__field",
        "template",
        "template__rlc__users",
        "template__standard_fields",
        "template__select_fields",
        "template__users_fields",
        "template__state_fields",
        "template__encrypted_file_fields",
        "template__encrypted_select_fields",
        "template__encrypted_standard_fields",
    ] + UNENCRYPTED_PREFETCH_RELATED

    ALL_ENTRY_TYPES = ENCRYPTED_ENTRY_TYPES + UNENCRYPTED_ENTRY_TYPES

    if TYPE_CHECKING:
        standard_entries: models.QuerySet["DataSheetStandardEntry"]
        encryptions: models.QuerySet["DataSheetEncryptionNew"]

    class Meta:
        ordering = ["-created"]
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self):
        return "record: {}; rlc: {};".format(self.pk, self.template.rlc.name)

    @property
    def org_pk(self) -> int:
        return self.template.rlc_id

    @property
    def actions(self):
        return {"OPEN": "/records/{}/".format(self.pk)}

    @property
    def identifier(self) -> str:
        entries = list(self.standard_entries.all())
        lowest_entry = None
        for entry in entries:
            if lowest_entry is None:
                lowest_entry = entry
            if entry.field.order < lowest_entry.field.order:
                lowest_entry = entry

        if lowest_entry:
            return lowest_entry.value

        return "NOT-SET"

    @property
    def attributes(self) -> dict[str, Union[list[str], str]]:
        entries: dict[str, Union[list[str], str]] = {
            "Created": localtime(self.created).strftime("%d.%m.%y %H:%M"),
            "Updated": localtime(self.updated).strftime("%d.%m.%y %H:%M"),
            "Name": self.name,
        }
        for entry_type in [
            "state_entries",
            "standard_entries",
            "multiple_entries",
            "select_entries",
            "users_entries",
        ]:
            for entry in getattr(self, entry_type).all():
                entries[entry.field.name] = entry.get_value()
        return entries

    def set_name(self, name: str):
        self.name = name
        self.folder.obj_renamed()

    def has_access(self, user: RlcUser) -> bool:
        if self.folder_uuid is None:
            for enc in getattr(self, "encryptions").all():
                if enc.user_id == user.id:
                    return True
        else:
            return self.folder.has_access(user)
        return False

    def generate_key(self, user: RlcUser):
        assert self.folder is not None

        if self.key is not None:
            raise ValueError("This record already has a key.")

        key = SymmetricKey.generate()
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def set_folder(self, folder: "Folder"):
        self.folder.put_obj_in_folder(folder)

    def get_aes_key(self, user: RlcUser, *args, **kwargs):
        assert self.folder is not None and self.key is not None
        decryption_key = self.folder.get_decryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        key = enc_key.decrypt(decryption_key)
        return key.get_key()

    def get_entries(self, user: RlcUser):
        entries = {}
        aes_key_record = self.get_aes_key(user)
        for entry_type in self.ALL_ENTRY_TYPES:
            for entry in getattr(self, entry_type).all():
                if entry.encrypted_entry:
                    entry.decrypt(aes_key_record=aes_key_record)
                entries[entry.field.name] = {
                    "id": entry.id,
                    "name": entry.field.name,
                    "type": entry.field.type,
                    "field": entry.field.pk,
                    "value": entry.get_raw_value(),
                }
        return entries

    def get_entries_new(self, user: RlcUser):
        entries = {}
        aes_key_record = self.get_aes_key(user)
        for entry_type in self.ALL_ENTRY_TYPES:
            for entry in getattr(self, entry_type).all():
                if entry.encrypted_entry:
                    entry.decrypt(aes_key_record=aes_key_record)
                entries[str(entry.field.uuid)] = entry.get_raw_value()
        return entries


###
# RecordEntry
###
class DataSheetEntry(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    view_name: str
    # used in record for get_entries
    encrypted_entry = False

    class Meta:
        abstract = True

    def get_raw_value(self):
        return self.get_value()

    def get_value(self, *args, **kwargs):
        raise NotImplementedError("This method needs to be implemented")


class DataSheetEntryEncryptedModelMixin(EncryptedModelMixin):
    encryption_class = AESEncryption
    # used in record for get entries
    encrypted_entry = True

    def encrypt(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        record: DataSheet = self.record  # type: ignore
        if user and not private_key_user:
            private_key_user = user.get_private_key()
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        super().encrypt(key)

    def decrypt(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        record: DataSheet = self.record  # type: ignore
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        super().decrypt(key)


class DataSheetStateEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="state_entries"
    )
    field = models.ForeignKey(
        DataSheetStateField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=1000)
    closed_at = models.DateTimeField(blank=True, null=True, default=None)
    view_name = "recordstateentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStateEntry"
        verbose_name_plural = "RecordStateEntries"

    def __str__(self):
        return "recordStateEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class DataSheetUsersEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="users_entries"
    )
    field = models.ForeignKey(
        DataSheetUsersField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.ManyToManyField(RlcUser, blank=True)
    view_name = "recordusersentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordUsersEntry"
        verbose_name_plural = "RecordUsersEntries"

    def __str__(self):
        return "recordUsersEntry: {};".format(self.pk)

    def get_raw_value(self):
        users = []
        for user in getattr(self, "value").all():
            users.append(user.pk)
        return users

    def get_value(self, *args, **kwargs):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        users = []
        for user in getattr(self, "value").all():
            users.append(user.name)
        return users


class DataSheetSelectEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="select_entries"
    )
    field = models.ForeignKey(
        DataSheetSelectField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=200)
    view_name = "recordselectentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordSelectEntry"
        verbose_name_plural = "RecordSelectEntries"

    def __str__(self):
        return "recordSelectEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class DataSheetMultipleEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="multiple_entries"
    )
    field = models.ForeignKey(
        DataSheetMultipleField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.JSONField()
    view_name = "recordmultipleentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordMultipleEntry"
        verbose_name_plural = "RecordMultipleEntries"

    def __str__(self):
        return "recordMultipleEntry: {}".format(self.pk)

    def get_value(self):
        return self.value


class DataSheetEncryptedSelectEntry(DataSheetEntryEncryptedModelMixin, DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="encrypted_select_entries"
    )
    field = models.ForeignKey(
        DataSheetEncryptedSelectField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.BinaryField()
    view_name = "recordencryptedselectentry-detail"

    # encryption
    encrypted_fields = ["value"]

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordEncryptedSelectEntry"
        verbose_name_plural = "RecordEncryptedSelectEntries"

    def __str__(self):
        return "recordEncryptedSelectEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == "ENCRYPTED":
            self.decrypt(*args, **kwargs)
        return self.value

    def encrypt(self, *args, **kwargs):
        self.value = json.dumps(self.value)
        super().encrypt(*args, **kwargs)

    def decrypt(self, *args, **kwargs):
        super().decrypt(*args, **kwargs)
        self.value = json.loads(self.value)


class DataSheetEncryptedFileEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="encrypted_file_entries"
    )
    field = models.ForeignKey(
        DataSheetEncryptedFileField, related_name="entries", on_delete=models.PROTECT
    )
    file = models.FileField(upload_to="recordmanagement/recordencryptedfileentry/")
    view_name = "recordencryptedfileentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordEncryptedFileEntry"
        verbose_name_plural = "RecordEncryptedFileEntries"

    def __str__(self):
        return "recordEncryptedFileEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.file.name.split("/")[-1].replace(".enc", "")

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    @staticmethod
    def encrypt_file(
        file,
        record: DataSheet,
        user: RlcUser | None = None,
        private_key_user=None,
        aes_key_record=None,
    ):
        if user and private_key_user:
            key = record.get_aes_key(
                user=user, private_key_user=private_key_user
            ).value_as_str
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        name = file.name
        file = AESEncryption.encrypt_in_memory_file(file, key)
        file = DjangoFile(file, name="{}.enc".format(name))
        return file

    def decrypt_file(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        if user and not private_key_user:
            private_key_user = user.get_private_key()
        if user and private_key_user:
            key = self.record.get_aes_key(
                user=user, private_key_user=private_key_user
            ).value_as_str
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        file = AESEncryption.decrypt_bytes_file(self.file, key)
        file.seek(0)
        return file


class DataSheetStandardEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="standard_entries"
    )
    field = models.ForeignKey(
        DataSheetStandardField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.TextField(max_length=20000)
    view_name = "recordstandardentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStandardEntry"
        verbose_name_plural = "RecordStandardEntries"

    def __str__(self):
        return "recordStandardEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class DataSheetEncryptedStandardEntry(
    DataSheetEntryEncryptedModelMixin, DataSheetEntry
):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="encrypted_standard_entries"
    )
    field = models.ForeignKey(
        DataSheetEncryptedStandardField,
        related_name="entries",
        on_delete=models.PROTECT,
    )
    value = models.BinaryField()
    view_name = "recordencryptedstandardentry-detail"

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ["value"]

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStandardEntry"
        verbose_name_plural = "RecordStandardEntries"

    def __str__(self):
        return "recordEncryptedStandardEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == "ENCRYPTED" or self.encryption_status is None:
            self.decrypt(*args, **kwargs)
        return self.value


class DataSheetStatisticEntry(DataSheetEntry):
    record = models.ForeignKey(
        DataSheet, on_delete=models.CASCADE, related_name="statistic_entries"
    )
    field = models.ForeignKey(
        DataSheetStatisticField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=200)
    view_name = "recordstatisticentry-detail"

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStatisticEntry"
        verbose_name_plural = "RecordStatisticEntries"

    def __str__(self):
        return "recordStatisticEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


###
# RecordEncryption
###
class DataSheetEncryptionNew(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        RlcUser, related_name="recordencryptions", on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        DataSheet, related_name="encryptions", on_delete=models.CASCADE
    )
    key = models.BinaryField()
    correct = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encryption_class = RSAEncryption
    encrypted_fields = ["key"]

    class Meta:
        unique_together = ["user", "record"]
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(
            self.pk, self.user.email, self.record.pk
        )

    def set_correct(self, value):
        key = DataSheetEncryptionNew.objects.get(pk=self.pk)
        key.correct = value
        key.save()
        self.correct = value

    def test(self, private_key_user):
        try:
            super().decrypt(private_key_user)
            self.set_correct(True)
        except ValueError:
            self.set_correct(False)
            self.user.locked = True
            self.user.save()

    def decrypt(self, private_key_user=None):
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        try:
            super().decrypt(key)
        except Exception as e:
            self.test(private_key_user)
            raise e

    def encrypt(self, public_key_user=None):
        if public_key_user:
            key = public_key_user
        else:
            raise ValueError("You need to pass (public_key_user).")
        super().encrypt(key)