#!/usr/bin/env bash

docker exec -t skylable/sxconsole-lite /srv/sxconsole-lite/manage.py \
    add_root_admin $1 $2
