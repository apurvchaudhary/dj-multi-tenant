from bson.objectid import ObjectId
from django.conf import settings

from mt_app.date_utils import time_now


class OrganizationMongoManager:
    def __init__(self):
        self.collection = settings.MONGO_DB["organization"]

    def create_organization(self, instance_id):
        document = {
            "organization_id": instance_id,
            "status": "pending",
            "db": "pending",
            "pod": "pending",
            "load_balancer": "pending",
        }
        result = self.collection.insert_one(document)
        return result.inserted_id

    def update_status_and_log(self, _id, key, status_update, log_message):
        try:
            update_query = {
                "$set": {key: status_update},
                "$push": {"updates.log": f"{time_now()} - {log_message}"},
            }
            self.collection.update_one({"_id": ObjectId(_id)}, update_query)
        except Exception as error:
            print(f"Error updating key '{key}': {error}")

    def update_organization(self, _id, data):
        result = self.collection.update_one({"_id": ObjectId(_id)}, {"$set": data})
        return result.modified_count

    def get_organization(self, _id):
        return self.collection.find_one({"_id": ObjectId(_id)})

    def get_all_organizations(self):
        return list(self.collection.find())

    def delete_organization(self, _id):
        return self.collection.delete_one({"_id": ObjectId(_id)}).deleted_count
