#!/usr/bin/env bash
# build.sh — Render build script
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

#!/usr/bin/env bash
# build.sh — Render build script
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser \
    --no-input \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || true
fi
