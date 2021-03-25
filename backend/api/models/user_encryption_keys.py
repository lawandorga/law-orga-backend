#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from backend.static.encryption import AESEncryption
from django_prometheus.models import ExportModelOperationsMixin
from backend.api.models.user import UserProfile
from django.db import models


class UserEncryptionKeys(
    ExportModelOperationsMixin("user_encryption_keys"), models.Model
):
    user = models.OneToOneField(
        UserProfile,
        related_name="encryption_keys",
        on_delete=models.CASCADE,
        null=False,
    )
    private_key = models.BinaryField()
    private_key_encrypted = models.BooleanField(default=False)
    public_key = models.BinaryField()

    class Meta:
        verbose_name = 'UserEncryptionKey'
        verbose_name_plural = 'UserEncryptionKeys'

    def __str__(self):
        return 'userEncryptionKey: {}; user: {};'.format(self.pk, self.user.email)

    def decrypt_private_key(self, key_to_encrypt: str) -> str:
        """
        decrypt the saved encrypted private key of the user with the given key, this key is the users 'normal' password

        if the private_key is not encrypted, it will be encrypted with the given key, still outputs the decrypted private key
        :param key_to_encrypt: users password
        :return: private key of the user
        """
        if not self.private_key_encrypted:
            self.private_key = AESEncryption.encrypt(self.private_key, key_to_encrypt)
            self.private_key_encrypted = True
            self.save()

        private_key = AESEncryption.decrypt(self.private_key, key_to_encrypt)
        return private_key
