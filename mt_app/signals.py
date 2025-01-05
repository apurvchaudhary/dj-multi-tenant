from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mt_app.models import Organization
from mt_app.mongo_utils import OrganizationMongoManager
from mt_app.tasks import setup_organization, delete_organization
from logging import info


@receiver(post_save, sender=Organization)
def handle_org(instance, created, **kwargs):
    if created:
        info(f"triggering {instance.name} creation task...")
        setup_organization.delay(instance.id)
        info(f"triggered {instance.name} creation task...")
    if instance.deleted:
        info(f"triggering {instance.name} deletion task...")
        delete_organization.delay(instance.id)
        info(f"triggered {instance.name} deletion task...")


@receiver(post_delete, sender=Organization)
def handle_org(instance, **kwargs):
    mongo_manager = OrganizationMongoManager()
    if instance.object_id:
        info(f"deleting {instance.name} from mongo...")
        mongo_manager.delete_organization(instance.object_id)
        info(f"deleted {instance.name} from mongo...")
