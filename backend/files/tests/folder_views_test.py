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

from unittest.mock import MagicMock

from django.test import TransactionTestCase
from rest_framework.test import APIClient

from backend.api.models import HasPermission, Permission
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.files.models import File, Folder, FolderPermission, PermissionForFolder
from backend.files.static.folder_permissions import PERMISSION_READ_FOLDER
from backend.static.encrypted_storage import EncryptedStorage
from backend.static.permissions import (
    PERMISSION_ACCESS_TO_FILES_RLC,
    PERMISSION_READ_ALL_FOLDERS_RLC,
)


class FolderViewsTest(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_base_fixtures()

        root_folder = Folder(
            name="files",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        root_folder.save()
        self.root_folder = root_folder
        middle_folder = Folder(
            name="ressorts",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=root_folder,
        )
        middle_folder.save()
        file = File(
            name="test file",
            creator=self.fixtures["users"][0]["user"],
            size=1000,
            folder=root_folder,
        )
        file.save()

    def test_get_folder_information(self):
        access_permission: Permission = Permission.objects.get(
            name=PERMISSION_ACCESS_TO_FILES_RLC
        )
        has_access_permission: HasPermission = HasPermission(
            permission=access_permission,
            group_has_permission=self.fixtures["groups"][0],
            permission_for_rlc=self.fixtures["rlc"],
        )
        has_access_permission.save()
        read_permission: Permission = Permission.objects.get(
            name=PERMISSION_READ_ALL_FOLDERS_RLC
        )
        has_read_permission: HasPermission = HasPermission(
            permission=read_permission,
            group_has_permission=self.fixtures["groups"][0],
            permission_for_rlc=self.fixtures["rlc"],
        )
        has_read_permission.save()

        client: APIClient = self.fixtures["users"][0]["client"]

        # check basic folder and files visibility
        response = client.get("/api/files/folder")
        self.assertEqual(200, response.status_code)
        self.assertIn("files", response.data)
        self.assertIn("folders", response.data)
        self.assertIn("write_permission", response.data)
        self.assertEqual(1, response.data["folders"].__len__())
        self.assertTrue(response.data["folders"][0]["name"] == "ressorts")
        self.assertEqual(1, response.data["files"].__len__())
        self.assertFalse(response.data["write_permission"])

        # added folder
        middle_folder_2 = Folder(
            name="vorlagen",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=self.root_folder,
        )
        middle_folder_2.save()

        response = client.get("/api/files/folder")
        self.assertEqual(2, response.data["folders"].__len__())

    def test_get_download_folder(self):
        response = self.fixtures["users"][0]["client"].get("/api/files/folder_download")
        self.assertEqual(400, response.status_code)

        access = Permission.objects.get(name=PERMISSION_ACCESS_TO_FILES_RLC)
        has_permission = HasPermission(
            permission=access,
            group_has_permission=self.fixtures["groups"][0],
            permission_for_rlc=self.fixtures["rlc"],
        )
        has_permission.save()

        EncryptedStorage.download_from_s3_and_decrypt_file = MagicMock()
        response = self.fixtures["users"][0]["client"].get("/api/files/folder_download")
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1, EncryptedStorage.download_from_s3_and_decrypt_file.call_count
        )
        a = 10
