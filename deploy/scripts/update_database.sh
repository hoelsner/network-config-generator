#!/usr/bin/env bash
export APP_SETTINGS="config.ProductionConfig"
export APP_SECRET_KEY="$(<'/var/www/network_config_generator/network_config_generator.key')"

# initialize migrations if necessary
cd "/var/www/network_config_generator"
if [ ! -d '/var/www/network_config_generator/migrations' ]; then
    sudo -u ncg -E venv/bin/python3 manage.py db init
fi
sudo -u ncg -E venv/bin/python3 manage.py db migrate
sudo -u ncg -E venv/bin/python3 manage.py db upgrade
