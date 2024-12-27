from django.contrib import admin, messages

from mt_app.models import CustomUser, Organization
from django.utils import timezone


admin.site.site_header = "Dashboard"
admin.site.site_title = "state manager admin"
admin.site.index_title = ""
admin.site.site_url = "/"


class OrganizationAdmin(admin.ModelAdmin):
    exclude = ('object_id', 'deleted_at', 'deleted_by', 'owner', 'deleted')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["subdomain"].disabled = True
            form.base_fields["subdomain"].help_text = "subdomain can not be updated"
        return form


    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return Organization.objects.filter(deleted=False)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.deleted_at = timezone.now()
        obj.deleted_by = request.user
        obj.save()

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.deleted:
            messages.error(request, f"Organization '{obj.name}' deletion task already in progress")
            return self.change_view(request, object_id, extra_context)
        return super().delete_view(request, object_id, extra_context)

admin.site.register(CustomUser)
admin.site.register(Organization, OrganizationAdmin)
