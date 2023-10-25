#!/bin/bash

source ./scripts/helpers.sh

if [[ "$1" == "docker" ]]; then
    docker run -it -p 8000:80 $DOCKER_IMAGE:latest;
else
    active_env
    cd src/
    uvicorn main:app --port 8000 --host 0.0.0.0 --reload
fi
