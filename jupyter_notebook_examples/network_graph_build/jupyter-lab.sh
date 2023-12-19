#!/usr/bin/env bash

PORT="`shuf -i 8888-9999 -n 1`"

docker run \
    -e "NB_UID=$UID" --user root \
    -e "GRANT_SUDO=yes" \
    -e DATA_DIR \
    -e STAGING_BUCKET \
    -e SCRATCHPAD_NOTEBOOK \
    --name 0109_chlamy_data_clustering_$(hostname)_$(id -u) \
    -w $PWD \
    -v $PWD:$PWD \
    -p $PORT:$PORT  -d --rm \
    -v $HOME/.aws:/home/jovyan/.aws \
    agbiome/0109_chlamy_data_clustering start.sh jupyter lab --allow-root --port $PORT
