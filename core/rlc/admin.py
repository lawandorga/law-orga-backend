from django.contrib import admin

from .forms import OrgAdminForm
from .models import Group, HasPermission, Note, Org, OrgEncryption, Permission


class HasPermissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


class UsersRlcKeysAdmin(admin.ModelAdmin):
    search_fields = ("rlc__name", "user__email")


class OrgAdmin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                ("Org", {"fields": ("name", "federal_state")}),
                ("Admin", {"fields": ("user_name", "user_email", "user_password")}),
            )
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = OrgAdminForm
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


admin.site.register(Note)
admin.site.register(Org, OrgAdmin)
admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(HasPermission, HasPermissionAdmin)
admin.site.register(OrgEncryption, UsersRlcKeysAdmin)