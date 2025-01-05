from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist

from mt_app.kube_utils import (
    deploy_pod,
    deploy_ingress,
    deploy_service,
    delete_pod,
    delete_service,
    delete_from_ingress,
)
from mt_app.models import Organization
from mt_app.mongo_utils import OrganizationMongoManager
from mt_app.psql_utils import create_schema, delete_schema
from mt_pro.celery import app


def send_websocket_update(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("updates", {"type": "send_update", "message": message})


def get_org_ws_msg(org_id, org_name, state, username):
    return {"org_id": org_id, "message": f"Organization {org_name} {state} by {username}"}


@app.task
def setup_organization(instance_id):
    try:
        instance = Organization.objects.get(id=instance_id)
    except ObjectDoesNotExist:
        return f"Organization not found with id {instance_id} for setup"
    else:
        status = []
        mongo_manager = OrganizationMongoManager()
        _id = mongo_manager.create_organization(instance_id=str(instance_id))
        instance.object_id = _id
        instance.save()
        for func in [create_schema, deploy_pod, deploy_service, deploy_ingress]:
            _bool, msg, key = func(instance.subdomain)
            status.append(_bool)
            mongo_manager.update_status_and_log(_id, key, "success" if _bool else "failed", msg)
            if not _bool:
                break
        mongo_manager.update_status_and_log(
            _id, "status", "success" if all(status) else "failed", "Your app is up & running!" if all(status) else
            "Issue occurred in initialisation!"
        )
        send_websocket_update(get_org_ws_msg(instance.id, instance.name, "created", instance.owner.username))
        return f"Organization {instance.name} setup done"


@app.task
def delete_organization(instance_id):
    try:
        instance = Organization.objects.select_related("owner").get(id=instance_id)
        org_name = instance.name
        username = instance.owner.username
    except ObjectDoesNotExist:
        return f"Organization not found with id {instance_id} for deletion"
    else:
        status = []
        mongo_manager = OrganizationMongoManager()
        _id = str(instance.object_id)
        for func in [delete_schema, delete_from_ingress, delete_service, delete_pod]:
            _bool, msg, key = func(instance.subdomain)
            status.append(_bool)
            mongo_manager.update_status_and_log(_id, key, "success" if _bool else "failed", msg)
        mongo_manager.update_status_and_log(
            _id, "status", "success" if all(status) else "failed", "Your app deleted successfully"
        )
        instance.delete()
        send_websocket_update(get_org_ws_msg(instance_id, org_name, "deleted", username))
        return f"Organization {instance.name} deletion done"
