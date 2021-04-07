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

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.files.models.file import File
from backend.files.models.folder import Folder
from backend.static.storage_folders import get_temp_storage_folder
from backend.static.storage_management import LocalStorageManager
from backend.static.middleware import get_private_key_from_request
from backend.static.error_codes import ERROR__FILES__FOLDER__CONTENT_DIDNT_EXIST


class DownloadViewSet(APIView):
    def post(self, request: Request) -> Response:
        users_private_key = get_private_key_from_request(request)
        aes_key = request.user.get_rlcs_aes_key(users_private_key)

        entries = request.data["entries"]
        request_path = request.data["path"]
        if request_path == "":
            request_path = "root"
        root_folder_name = get_temp_storage_folder() + "/" + request_path

        for entry in entries:
            # file
            if entry["type"] == 1:
                file = File.objects.get(pk=entry["id"])
                if file.folder.user_has_permission_read(request.user):
                    file.download(aes_key, root_folder_name)
            # folder
            else:
                folder = Folder.objects.get(pk=entry["id"])
                if folder.user_has_permission_read(request.user):
                    folder.download_folder(aes_key, root_folder_name)
        if LocalStorageManager.delete_folder_if_empty(root_folder_name):
            LocalStorageManager.delete_folder_if_empty(get_temp_storage_folder())
            raise CustomError(ERROR__FILES__FOLDER__CONTENT_DIDNT_EXIST)

        LocalStorageManager.zip_folder_and_delete(root_folder_name, root_folder_name)
        return LocalStorageManager.create_response_from_zip_file(
            root_folder_name + ".zip"
        )
