#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2021  Dominik Walser
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

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.recordmanagement.models import Tag, EncryptedRecord


class RecordStatisticsViewSet(APIView):
    def get(self, request: Request):
        record_tags = Tag.objects.all()
        out_tags = []
        for tag in record_tags:
            out_tags.append(
                {
                    "name": tag.name,
                    "value": tag.records.filter(from_rlc=request.user.rlc).count(),
                }
            )

        rlc_records: [EncryptedRecord] = EncryptedRecord.objects.filter(
            from_rlc=request.user.rlc
        )
        total_records = rlc_records.count()
        total_records_open = rlc_records.filter(state="op").count()
        total_records_waiting = rlc_records.filter(state="wa").count()
        total_records_closed = rlc_records.filter(state="cl").count()
        total_records_working = rlc_records.filter(state="wo").count()

        return Response(
            {
                "tags": out_tags,
                "records": {
                    "overall": total_records,
                    "states": [
                        {"name": "open", "value": total_records_open},
                        {"name": "waiting", "value": total_records_waiting},
                        {"name": "closed", "value": total_records_closed},
                        {"name": "working", "value": total_records_working},
                    ],
                },
            }
        )
