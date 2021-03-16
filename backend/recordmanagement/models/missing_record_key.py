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

from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
from backend.api.models import UserProfile
from backend.recordmanagement.models.encrypted_record import EncryptedRecord


class MissingRecordKey(ExportModelOperationsMixin("missing_record_key"), models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="missing_record_keys", on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        EncryptedRecord, related_name="missing_record_keys", on_delete=models.CASCADE
    )

    def __str__(self):
        return (
            "missing records keys, user: "
            + str(self.user)
            + "; record: "
            + str(self.record)
        )
