#!/bin/bash
set -e

if [ "$1" != "gunicorn" ] && [[ "$1" != *"wsgi:"* ]]; then
  echo "⏩ Ejecutando comando manual: $@"
  exec "$@"
fi

echo "🔄 Ejecutando migraciones..."
flask db upgrade

echo "🌱 Ejecutando seed..."
python seed_admin.py

echo "🚀 Iniciando Gunicorn..."
exec gunicorn -b 0.0.0.0:5050 'app:create_app()'
