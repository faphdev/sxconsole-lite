#!/bin/bash -x

echo "Downloading images..."
docker pull skylable/sxconsole-lite || exit 1
docker pull skylable/sxconsole-graphite || exit 1

mkdir -p /data/sxconsole-lite/
# Generate conf if sxconsole-lite is ran for the first time
if [ ! -e /data/sxconsole-lite/conf_defaults.yaml ]; then
    echo "Could not find sxconsole configuration file (/data/sxconsole-lite/conf_defaults.yaml)"
    echo "Generating configuration file..."
    ./generate_conf.py
fi

# Generate ssl cert
if [ ! -e /data/sxconsole-lite/sxconsole-lite.crt ]; then
    echo "Could not find SSL certs in /data/sxconsole-lite/"
    echo "Generating self-signed certs..."
    openssl genrsa -out ca.key 2048
    openssl req -new -key ca.key -out ca.csr
    openssl x509 -req -days 3650 -in ca.csr -signkey ca.key -out ca.crt
    mv ca.crt /data/sxconsole-lite/sxconsole-lite.crt
    mv ca.key /data/sxconsole-lite/sxconsole-lite.key
fi

echo "Starting containers..."
set -e
docker run -d \
    -v /data/sxconsole-graphite:/var/lib/graphite/storage/whisper \
    --name=sxconsole-graphite \
    skylable/sxconsole-graphite

docker run -d \
    -v /data/sxconsole-lite:/data \
    -v /data/sxconsole-graphite:/var/lib/graphite/storage/whisper \
    -v /data/sxconsole-lite/logs:/srv/logs \
    -p :8888:443 \
    --name=sxconsole-lite \
    --link sxconsole-graphite:sxconsole-graphite \
    skylable/sxconsole-lite

docker ps
