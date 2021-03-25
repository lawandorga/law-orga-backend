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


class EncryptedRecordPermission(
    ExportModelOperationsMixin("encrypted_record_permission"), models.Model
):
    request_from = models.ForeignKey(
        UserProfile,
        related_name="e_record_permissions_requested",
        on_delete=models.CASCADE,
        null=False,
    )
    request_processed = models.ForeignKey(
        UserProfile,
        related_name="e_record_permissions_processed",
        on_delete=models.SET_NULL,
        null=True,
    )

    record = models.ForeignKey(
        "EncryptedRecord",
        related_name="e_permissions_requested",
        on_delete=models.CASCADE,
        null=False,
    )

    requested = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True)
    can_edit = models.BooleanField(default=False)

    encrypted_record_permission_states_possible = (
        ("re", "requested"),
        ("gr", "granted"),
        ("de", "declined"),
    )
    state = models.CharField(
        max_length=2, choices=encrypted_record_permission_states_possible, default="re"
    )

    class Meta:
        verbose_name = 'RecordPermission'
        verbose_name_plural = 'RecordPermissions'

    def __str__(self):
        return "recordPermission: {}; from: {};".format(self.id, self.request_from.email)
