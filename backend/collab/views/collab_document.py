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

from typing import Any
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from backend.collab.models import (
    CollabDocument,
    PermissionForCollabDocument,
)
from backend.collab.serializers import (
    CollabDocumentPermissionListSerializer,
    CollabDocumentSerializer,
    CollabDocumentTreeSerializer,
)
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__ID_NOT_FOUND


class CollabDocumentListViewSet(viewsets.ModelViewSet):
    queryset = CollabDocument.objects.all()

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(rlc=self.request.user.rlc)

    def list(self, request: Request, **kwargs: Any) -> Response:
        queryset = self.get_queryset().exclude(path__contains="/").order_by("path")
        data = CollabDocumentTreeSerializer(
            instance=queryset,
            user=request.user,
            all_documents=self.get_queryset(),
            many=True,
            context={request: request},
        ).data
        return Response(data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data = request.data

        if "parent_id" in data and data["parent_id"] != None:
            try:
                parent = CollabDocument.objects.get(pk=data["parent_id"])
            except:
                raise CustomError(ERROR__API__ID_NOT_FOUND)
        else:
            parent = None

        new_document = CollabDocument(
            rlc=request.user.rlc,
            name=data["name"],
            parent=parent,
            creator=request.user,
            last_editor=request.user,
        )
        CollabDocument.create_or_duplicate(new_document)

        return Response(CollabDocumentSerializer(new_document).data)

    @action(detail=True, methods=["get"])
    def permissions(self, request: Request, pk: int):
        permissions = PermissionForCollabDocument.objects.filter(document__id=pk)
