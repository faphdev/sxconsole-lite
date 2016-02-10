#! /bin/sh

sudo pip install whisper
sudo pip install carbon
sudo chown -R sxconsole:sxconsole /opt/graphite/conf /opt/graphite/storage
cp config/carbon.conf config/storage-schemas.conf config/storage-aggregation.conf /opt/graphite/conf
python /opt/graphite/bin/carbon-cache.py start
