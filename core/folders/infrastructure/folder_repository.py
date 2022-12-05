from uuid import UUID

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.value_objects.tree import FolderTree
from core.folders.models import FoldersFolder


class DjangoFolderRepository(FolderRepository):
    @classmethod
    def get_cache_key(cls, org_pk: int):
        return "random39547294757{}".format(org_pk)

    @classmethod
    def __as_dict(cls, org_pk: int) -> dict[UUID, FoldersFolder]:
        folders = {}
        for f in list(FoldersFolder.query().filter(org_id=org_pk, deleted=False)):
            folders[f.uuid] = f
        return folders

    @classmethod
    def __users(cls, org_pk: int) -> dict[UUID, RlcUser]:
        users = {}
        for u in list(RlcUser.objects.filter(org_id=org_pk)):
            users[u.uuid] = u
        return users

    @classmethod
    def get_or_create_records_folder(cls, org_pk: int, user: IOwner) -> Folder:
        name = "Records"
        if FoldersFolder.objects.filter(
            org_id=org_pk, name=name, _parent=None
        ).exists():
            f = FoldersFolder.objects.get(org_id=org_pk, name=name, _parent=None)
            return cls.dict(org_pk)[f.uuid]
        folder = Folder.create(name=name, org_pk=org_pk)
        folder.grant_access(user)
        for u in RlcUser.objects.filter(org_id=org_pk).exclude(uuid=user.uuid):
            folder.grant_access(u, user)
        cls.save(folder)
        return cls.dict(org_pk)[folder.uuid]

    @classmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        folders = cls.dict(org_pk)
        if uuid in folders:
            return folders[uuid]
        raise ObjectDoesNotExist()

    @classmethod
    def dict(cls, org_pk: int) -> dict[UUID, Folder]:
        cache_value = cache.get(cls.get_cache_key(org_pk), None)
        if cache_value:
            return cache_value

        folders = cls.__as_dict(org_pk)
        domain_folders = {}
        for i, f in folders.items():
            domain_folders[i] = f.to_domain(folders, cls.__users(org_pk))

        cache.set(cls.get_cache_key(org_pk), domain_folders)

        return domain_folders

    @classmethod
    def list(cls, org_pk: int) -> list[Folder]:
        folders = cls.__as_dict(org_pk)
        folders_list = []
        for folder in folders.values():
            folders_list.append(folder.to_domain(folders, cls.__users(org_pk)))
        return folders_list

    @classmethod
    def save(cls, folder: Folder):
        FoldersFolder.from_domain(folder).save()
        cache.delete(cls.get_cache_key(folder.org_pk))

    @classmethod
    def delete(cls, folder: Folder):
        f = FoldersFolder.from_domain(folder)
        f.deleted = True
        f.deleted_at = timezone.now()
        f.save()
        cache.delete(cls.get_cache_key(folder.org_pk))

    @classmethod
    def tree(cls, org_pk: int) -> FolderTree:
        return FolderTree(cls.list(org_pk))
