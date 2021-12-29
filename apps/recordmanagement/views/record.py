import mimetypes

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.http import FileResponse
from rest_framework.exceptions import ParseError, APIException

from apps.recordmanagement.serializers import RecordDocumentSerializer
from apps.recordmanagement.serializers.record import RecordTemplateSerializer, RecordEncryptedStandardFieldSerializer, \
    RecordSerializer, RecordEncryptedStandardEntrySerializer, RecordStandardEntrySerializer, \
    RecordEncryptedFileEntrySerializer, RecordStandardFieldSerializer, RecordEncryptedFileFieldSerializer, \
    RecordEncryptedSelectFieldSerializer, RecordEncryptedSelectEntrySerializer, RecordUsersFieldSerializer, \
    RecordUsersEntrySerializer, RecordStateFieldSerializer, \
    RecordStateEntrySerializer, RecordSelectEntrySerializer, RecordSelectFieldSerializer, RecordListSerializer, \
    RecordDetailSerializer, RecordCreateSerializer, RecordMultipleEntrySerializer, RecordMultipleFieldSerializer, \
    FIELD_TYPES_AND_SERIALIZERS
from apps.recordmanagement.models.record import RecordTemplate, RecordEncryptedStandardField, Record, \
    RecordEncryptionNew, RecordEncryptedStandardEntry, RecordStandardEntry, RecordEncryptedFileEntry, \
    RecordStandardField, RecordEncryptedFileField, \
    RecordEncryptedSelectField, RecordEncryptedSelectEntry, RecordUsersField, RecordUsersEntry, RecordStateField, \
    RecordStateEntry, RecordSelectEntry, RecordSelectField, RecordMultipleEntry, RecordMultipleField
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from apps.static.encryption import AESEncryption
from rest_framework import status, mixins


###
# Template
###
class RecordTemplateViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                            mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RecordTemplate.objects.none()
    serializer_class = RecordTemplateSerializer

    def get_queryset(self):
        return RecordTemplate.objects.filter(rlc=self.request.user.rlc)

    @action(detail=True, methods=['get'])
    def fields(self, request, *args, **kwargs):
        instance = self.get_object()
        fields = instance.get_fields(FIELD_TYPES_AND_SERIALIZERS, request=request)
        return Response(fields)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ParseError('There are records that use this template. '
                             'You can only delete templates that are not used.')


###
# Fields
###
class RecordFieldViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                         GenericViewSet):
    model = None

    def get_queryset(self):
        return self.model.objects.filter(template__rlc=self.request.user.rlc)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ParseError('This field has associated data from one or more records. '
                             'At the moment there is no way to delete this field.')


class RecordStateFieldViewSet(RecordFieldViewSet):
    queryset = RecordStateField.objects.none()
    serializer_class = RecordStateFieldSerializer
    model = RecordStateField


class RecordEncryptedStandardFieldViewSet(RecordFieldViewSet):
    queryset = RecordEncryptedStandardField.objects.none()
    serializer_class = RecordEncryptedStandardFieldSerializer
    model = RecordEncryptedStandardField


class RecordStandardFieldViewSet(RecordFieldViewSet):
    queryset = RecordStandardField.objects.none()
    serializer_class = RecordStandardFieldSerializer
    model = RecordStandardField


class RecordSelectFieldViewSet(RecordFieldViewSet):
    queryset = RecordSelectField.objects.none()
    serializer_class = RecordSelectFieldSerializer
    model = RecordSelectField


class RecordMultipleFieldViewSet(RecordFieldViewSet):
    queryset = RecordMultipleField.objects.none()
    serializer_class = RecordMultipleFieldSerializer
    model = RecordMultipleField


class RecordEncryptedFileFieldViewSet(RecordFieldViewSet):
    queryset = RecordEncryptedFileField.objects.none()
    serializer_class = RecordEncryptedFileFieldSerializer
    model = RecordEncryptedFileField


class RecordEncryptedSelectFieldViewSet(RecordFieldViewSet):
    queryset = RecordEncryptedSelectField.objects.none()
    serializer_class = RecordEncryptedSelectFieldSerializer
    model = RecordEncryptedSelectField


class RecordUsersFieldViewSet(RecordFieldViewSet):
    queryset = RecordUsersField.objects.none()
    serializer_class = RecordUsersFieldSerializer
    model = RecordUsersField


###
# Record
###
class RecordViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                    GenericViewSet):
    queryset = Record.objects.none()
    serializer_class = RecordSerializer

    def get_serializer_class(self):
        if self.action in ['list']:
            return RecordListSerializer
        elif self.action in ['retrieve']:
            return RecordDetailSerializer
        elif self.action in ['create']:
            return RecordCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ['list']:
            return Record.objects.filter(template__rlc=self.request.user.rlc).prefetch_related(
                'state_entries', 'state_entries__field',
                'select_entries', 'select_entries__field',
                'standard_entries', 'standard_entries__field',
                'users_entries', 'users_entries__value', 'users_entries__field',
                'multiple_entries', 'multiple_entries__field',
                'encryptions'
            ).select_related('template')
        elif self.action in ['retrieve']:
            return Record.objects.filter(template__rlc=self.request.user.rlc).prefetch_related(
                'state_entries', 'state_entries__field',
                'select_entries', 'select_entries__field',
                'standard_entries', 'standard_entries__field',
                'multiple_entries', 'multiple_entries__field',
                'users_entries', 'users_entries__field', 'users_entries__value',
                'encrypted_select_entries', 'encrypted_select_entries__field',
                'encrypted_standard_entries', 'encrypted_standard_entries__field',
                'encrypted_file_entries', 'encrypted_file_entries__field',
                'template',
                'template__standard_fields',
                'template__select_fields',
                'template__users_fields',
                'template__state_fields',
                'template__encrypted_file_fields',
                'template__encrypted_select_fields',
                'template__encrypted_standard_fields',
            ).select_related('old_client')
        return Record.objects.filter(template__rlc=self.request.user.rlc)

    def perform_create(self, serializer):
        record = serializer.save()
        aes_key = AESEncryption.generate_secure_key()
        public_key_user = self.request.user.get_public_key()
        encryption = RecordEncryptionNew(record=record, user=self.request.user, key=aes_key)
        encryption.encrypt(public_key_user=public_key_user)
        encryption.save()

    @action(detail=True, methods=['get'])
    def documents(self, request, *args, **kwargs):
        record = self.get_object()
        documents = record.documents.all()
        return Response(RecordDocumentSerializer(documents, many=True).data)


###
# Entry
###
class RecordEncryptedSelectEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                        GenericViewSet):
    queryset = RecordEncryptedSelectEntry.objects.none()
    serializer_class = RecordEncryptedSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedSelectEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        entry = RecordEncryptedSelectEntry(**serializer.validated_data)
        entry.encrypt(user=request.user, private_key_user=private_key_user)
        entry.save()
        serializer = self.get_serializer(instance=entry, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        self.instance = super().get_object()
        return self.instance

    def perform_update(self, serializer):
        for attr, value in serializer.validated_data.items():
            setattr(self.instance, attr, value)
        private_key_user = self.request.user.get_private_key(request=self.request)
        self.instance.encrypt(user=self.request.user, private_key_user=private_key_user)
        self.instance.save()
        self.instance.decrypt(user=self.request.user, private_key_user=private_key_user)


class RecordEncryptedFileEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                      GenericViewSet):
    queryset = RecordEncryptedFileEntry.objects.none()
    serializer_class = RecordEncryptedFileEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedFileEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    @action(detail=True, methods=['get'])
    def download(self, request, *args, **kwargs):
        instance = self.get_object()
        private_key_user = request.user.get_private_key(request=request)
        file = instance.decrypt_file(private_key_user=private_key_user, user=request.user)
        response = FileResponse(file, content_type=mimetypes.guess_type(instance.get_value())[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.get_value())
        return response


class RecordStandardEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 GenericViewSet):
    queryset = RecordStandardEntry.objects.none()
    serializer_class = RecordStandardEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStandardEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordSelectEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                               GenericViewSet):
    queryset = RecordSelectEntry.objects.none()
    serializer_class = RecordSelectEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordSelectEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordMultipleEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                 GenericViewSet):
    queryset = RecordMultipleEntry.objects.none()
    serializer_class = RecordMultipleEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordMultipleEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordStateEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordStateEntry.objects.none()
    serializer_class = RecordStateEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordStateEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordUsersEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecordUsersEntry.objects.none()
    serializer_class = RecordUsersEntrySerializer

    def get_queryset(self):
        # every field returned because they are supposed to be seen by everybody
        return RecordUsersEntry.objects.filter(record__template__rlc=self.request.user.rlc)


class RecordEncryptedStandardEntryViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                          GenericViewSet):
    queryset = RecordEncryptedStandardEntry.objects.none()
    serializer_class = RecordEncryptedStandardEntrySerializer

    def get_queryset(self):
        # every field returned because they will be encrypted by default
        return RecordEncryptedStandardEntry.objects.filter(record__template__rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        private_key_user = request.user.get_private_key(request=request)
        record = serializer.validated_data['record']
        aes_key_record = record.get_aes_key(request.user, private_key_user)
        entry = RecordEncryptedStandardEntry(**serializer.validated_data)
        entry.encrypt(aes_key_record=aes_key_record)
        entry.save()
        entry.decrypt(aes_key_record=aes_key_record)
        serializer = self.get_serializer(instance=entry, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        self.instance = super().get_object()
        return self.instance

    def perform_update(self, serializer):
        for attr, value in serializer.validated_data.items():
            setattr(self.instance, attr, value)
        private_key_user = self.request.user.get_private_key(request=self.request)
        aes_key_record = self.instance.record.get_aes_key(user=self.request.user, private_key_user=private_key_user)
        self.instance.encrypt(aes_key_record=aes_key_record)
        self.instance.save()
        self.instance.decrypt(user=self.request.user, aes_key_record=aes_key_record)
