from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from mt_app.models import Organization
from mt_app.mongo_utils import OrganizationMongoManager


@receiver(post_save, sender=Organization)
def handle_org(sender, instance, created, **kwargs):
    if created:
        mongo_manager = OrganizationMongoManager()
        _id = mongo_manager.create_organization(
            organization_id=str(instance.id),
            pod_name="pod_name",
            service_name="service_name",
            db_schema="db_schema"
        )
        instance.object_id = _id
        instance.save()


@receiver(post_delete, sender=Organization)
def handle_org(sender, instance, **kwargs):
    mongo_manager = OrganizationMongoManager()
    if instance.object_id:
        mongo_manager.delete_organization(instance.object_id)
