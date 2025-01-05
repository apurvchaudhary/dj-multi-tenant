#!/bin/sh
# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
yes | python manage.py collectstatic --clear --noinput

echo "Setting up defaults"
python manage.py create_default_groups
python manage.py create_super_user

exec "$@"