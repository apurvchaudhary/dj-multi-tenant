from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "get or create default groups with specific permissions"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="member")
        if created:
            permissions = Permission.objects.filter(
                codename__in=[
                    "add_organization",
                    "change_organization",
                    "delete_organization",
                    "view_organization",
                ]
            )
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f"Group member created successfully"))
