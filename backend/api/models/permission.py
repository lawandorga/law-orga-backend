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
from django.db import models


class Permission(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return 'permission: {}; name: {};'.format(self.pk, self.name)

    def get_groups_with_permission_from_rlc(self, rlc):
        from backend.api.models import Group, HasPermission

        groups = Group.objects.filter(from_rlc=rlc)
        return HasPermission.objects.filter(
            permission=self,
            group_has_permission__in=groups.values_list("pk", flat=True),
        )

    def get_users_with_permission_from_rlc(self, rlc):
        """
        TODO: rename this method, return not users but HasPermissions
        :param rlc:
        :return:
        """
        from backend.api.models import UserProfile, HasPermission

        users = UserProfile.objects.filter(rlc=rlc)
        return HasPermission.objects.filter(
            permission=self, user_has_permission__in=users.values_list("pk", flat=True)
        )

    def get_rlc_permissions_with_special_permission(self, rlc):
        from backend.api.models import HasPermission

        return HasPermission.objects.filter(permission=self, rlc_has_permission=rlc)

    def get_real_users_with_permission_for_rlc(self, rlc):
        # TODO: add permission_for_rlc?
        from backend.api.models import UserProfile, HasPermission

        if HasPermission.objects.filter(rlc_has_permission=rlc, permission=self):
            return UserProfile.objects.filter(rlc=rlc)
        users = UserProfile.objects.filter(
            user_has_permission__permission=self, rlc=rlc
        )
        group_users = UserProfile.objects.filter(
            group_members__group_has_permission__permission=self, rlc=rlc
        ).distinct()
        return users.union(group_users).distinct()
