from django.db import connection
from django.db.utils import ProgrammingError


def create_schema(schema_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_name}'")
            if cursor.fetchone():
                return False, f"DB '{schema_name}' already exists."
            cursor.execute(f"CREATE SCHEMA {schema_name}")
            return True, f"DB '{schema_name}' created successfully."
    except ProgrammingError as error:
        return False, f"Error in creating DB '{schema_name}' {error}"


def delete_schema(schema_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = {schema_name}")
            if not cursor.fetchone():
                return False, f"DB '{schema_name}' does not exists for deletion."
            cursor.execute(f"DROP SCHEMA {schema_name} CASCADE")
            return True, f"DB '{schema_name}' deleted successfully."
    except Exception as error:
        return False, f"Error in deleting DB '{schema_name}' {error}"
