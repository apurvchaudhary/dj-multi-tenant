from django.conf import settings
from bson.objectid import ObjectId


class OrganizationMongoManager:
    def __init__(self):
        self.collection = settings.MONGO_DB['organization']

    def create_organization(self, organization_id, pod_name, service_name, db_schema):
        document = {
            "organization_id": organization_id,
            "pod_name": pod_name,
            "service_name": service_name,
            "db_schema": db_schema
        }
        result = self.collection.insert_one(document)
        return result.inserted_id

    def update_organization(self, _id, data):
        object_id = ObjectId(_id)
        result = self.collection.update_one(
            {"_id": object_id},
            {"$set": data}
        )
        return result.modified_count

    def get_organization(self, _id):
        object_id = ObjectId(_id)
        return self.collection.find_one({"_id": object_id})

    def get_all_organizations(self):
        return list(self.collection.find())

    def delete_organization(self, _id):
        object_id = ObjectId(_id)
        return self.collection.delete_one({"_id": object_id}).deleted_count
