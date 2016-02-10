#!/bin/bash -x

# start SXConsole
RUN_AS=sxconsole
SUGGEST_CMD="docker run -v /path/to/datadir:/data --name=sxconsole-lite --link sxconsole-lite-graphite:sxconsole-lite-graphite --restart=always -d sxconsole-lite"

for i in sxconsole-lite.key sxconsole-lite.crt; do
    if ! [ -r /data/$i ]; then
        echo $i not found. Please use the following syntax and make sure the sxconsole user can read the file:
        echo Use: $SUGGEST_CMD
        exit 1
    fi
done

echo Copying SSL certs...
mkdir -p /etc/nginx/ssl
cp /data/sxconsole-lite.crt /data/sxconsole-lite.key /etc/nginx/ssl/
chmod 600 /etc/nginx/ssl/sxconsole-lite.key

echo Updating SXConsole config file...
mkdir -p /data/sql

if ! [ -r "/data/conf_defaults.yaml" ]; then
    # call the script here
    cp /srv/sxconsole-lite/conf_example.yaml /data/conf_defaults.yaml
else
    chmod 600 /data/conf_defaults.yaml
    cp -p /data/conf_defaults.yaml /srv/sxconsole-lite/conf.yaml
fi

if grep -i ^Edit-me-first /srv/sxconsole-lite/conf.yaml; then
    echo Please edit conf_defaults.yaml
    exit 1
fi

if [ -z "$SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR" ]; then
    # is the container linked with a different name? Guess
    export $(env|grep PORT_2004_TCP_ADDR=|head -n 1|sed -e 's/^.*PORT_2004_TCP_ADDR/SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR/')
fi
if [ -z "$SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR" ]; then
    echo You must link this container to sxconsole-lite-graphite
    echo Use: $SUGGEST_CMD
    exit 1
fi
sed -i "s/CARBON_ADDR/$SXCONSOLE_GRAPHITE_PORT_2004_TCP_ADDR/" /srv/sxconsole-lite/conf.yaml

echo Building static assets
webpack -p

# Create sxconsole user
if ! getent passwd $RUN_AS > /dev/null 2>&1; then
    adduser $RUN_AS
fi

echo Starting migrate and collectstatic
python manage.py migrate                  # Apply database migrations

# Apply secure permissions to the db
chown -R $RUN_AS /data/sql
chmod -R go-rwx /data/sql

python manage.py compilemessages          # Compile translations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
mkdir -p /srv/logs
mkdir -p /srv/logs/supervisor
chown -R $RUN_AS /srv/logs
touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &
chown -R $RUN_AS /srv



echo If you need to add a root admin, run:
echo 'docker exec -t -i  sxconsole-lite su sxconsole -c "/srv/sxconsole-lite/manage.py add_root_admin your-email your-pass"'

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf

