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

from rest_framework.viewsets import ModelViewSet

from backend.api.permissions import OnlySuperuser
from backend.api.models import RlcEncryptionKeys
from backend.api.serializers import RlcEncryptionKeysSerializer


# TODO: Why define a ModelViewSet only for superuser? When is this used in the real world?
class RlcEncryptionKeysViewSet(ModelViewSet):
    queryset = RlcEncryptionKeys.objects.all()
    serializer_class = RlcEncryptionKeysSerializer
    permission_classes = (OnlySuperuser,)
