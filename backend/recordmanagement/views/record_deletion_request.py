#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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

from datetime import datetime

import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.recordmanagement import models, serializers
from backend.recordmanagement.models.record_deletion_request import RecordDeletionRequest
from backend.static import error_codes, permissions


class RecordDeletionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecordDeletionRequestSerializer
    queryset = RecordDeletionRequest.objects.all()

    def list(self, request, *args, **kwargs):
        if (
            not request.user.has_permission(
                permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
                for_rlc=request.user.rlc,
            )
            and not request.user.is_superuser
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        if request.user.is_superuser:
            queryset = RecordDeletionRequest.objects.all()
        else:
            queryset = RecordDeletionRequest.objects.filter(
                request_from__rlc=request.user.rlc
            )
        return Response(
            serializers.RecordDeletionRequestSerializer(queryset, many=True).data
        )

    def create(self, request):
        if "record_id" not in request.data:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__ID_NOT_PROVIDED)

        record = EncryptedRecord.objects.get_record(
            request.user, request.data["record_id"]
        )
        if not record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        if (
            RecordDeletionRequest.objects.filter(
                record=record, state="re"
            ).count()
            >= 1
        ):
            raise CustomError(
                error_codes.ERROR__RECORD__RECORD_DELETION__ALREADY_REQUESTED
            )
        deletion_request = RecordDeletionRequest(
            request_from=request.user,
            record=record,
            explanation=request.data["explanation"],
        )
        if "explanation" in request.data:
            deletion_request.explanation = request.data["explanation"]
        deletion_request.save()
        return Response(
            serializers.RecordDeletionRequestSerializer(deletion_request).data
        )


class RecordDeletionProcessViewSet(APIView):
    def post(self, request):
        user = request.user
        if not user.has_permission(
            permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS, for_rlc=user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if "request_id" not in request.data:
            raise CustomError(error_codes.ERROR__API__ID_NOT_PROVIDED)
        try:
            record_deletion_request = RecordDeletionRequest.objects.get(
                pk=request.data["request_id"]
            )
        except:
            raise CustomError(error_codes.ERROR__RECORD__DELETION_REQUEST__NOT_EXISTING)

        if "action" not in request.data:
            raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)
        action = request.data["action"]
        if action != "accept" and action != "decline":
            raise CustomError(error_codes.ERROR__API__ACTION_NOT_VALID)

        record_deletion_request.request_processed = user
        record_deletion_request.processed_on = datetime.utcnow().replace(
            tzinfo=pytz.utc
        )
        if action == "accept":
            if record_deletion_request.state == "re":
                record_deletion_request.state = "gr"
                record_deletion_request.save()
            record_deletion_request.record.delete()
        else:
            record_deletion_request.state = "de"
            record_deletion_request.save()
        response_request = RecordDeletionRequest.objects.get(
            pk=record_deletion_request.id
        )
        return Response(
            serializers.RecordDeletionRequestSerializer(response_request).data
        )
