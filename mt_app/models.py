from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.manager import Manager


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = [("superuser", "Superuser"), ("member", "Member")]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")

    def __str__(self):
        return f"{self.username}"

    def save(self, *args, **kwargs):
        if self.role == "member" and not self.pk:
            super().save(*args, **kwargs)
            group = Group.objects.get(name="member")
            self.groups.add(group)
        super().save(*args, **kwargs)


class Organization(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owned_organizations")
    description = models.TextField(null=True, blank=True, help_text="Do not add sensitive information")
    subdomain = models.CharField(max_length=12, help_text="if given 'test' url will be: https://test.host.com")
    name = models.CharField(max_length=100, unique=True, help_text="Your organization name")
    object_id = models.CharField(max_length=24, unique=True, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, default=None)
    deleted_by = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, default=None)

    objects = Manager()

    def __str__(self):
        return self.name
