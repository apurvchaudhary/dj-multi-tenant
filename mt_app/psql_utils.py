from django.db import connection
from django.db.utils import ProgrammingError


def create_schema(schema_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_name}';")
            if cursor.fetchone():
                return True, f"DB '{schema_name}' already exists."
            cursor.execute(f"CREATE SCHEMA {schema_name};")
            return True, f"DB created successfully.", "db"
    except ProgrammingError as error:
        return False, f"Error in creating DB {error}", "db"


def delete_schema(schema_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_name}';")
            if not cursor.fetchone():
                return True, f"DB '{schema_name}' does not exists for deletion.", "db"
            cursor.execute(f"DROP SCHEMA {schema_name} CASCADE;")
            return True, f"DB deleted successfully.", "db"
    except Exception as error:
        return False, f"Error in deleting DB {error}", "db"
