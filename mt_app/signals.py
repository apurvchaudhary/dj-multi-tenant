from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mt_app.models import Organization
from mt_app.mongo_utils import OrganizationMongoManager
from mt_app.psql_utils import create_schema


@receiver(post_save, sender=Organization)
def handle_org(instance, created, **kwargs):
    if created:
        mongo_manager = OrganizationMongoManager()
        _id = mongo_manager.create_organization(instance_id=str(instance.id))
        _bool, msg = create_schema(instance.subdomain)
        mongo_manager.update_status_and_log(_id, "db", "success" if _bool else "failed", msg)


@receiver(post_delete, sender=Organization)
def handle_org(instance, **kwargs):
    mongo_manager = OrganizationMongoManager()
    if instance.object_id:
        mongo_manager.delete_organization(instance.object_id)
