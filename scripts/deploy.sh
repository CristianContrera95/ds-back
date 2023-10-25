#!/bin/bash

source ./scripts/helpers.sh

if [[ "$CONTAINER_REGISTRY" == "" ]]; then
    CONTAINER_REGISTRY="machinelearningresearch.azurecr.io"
fi

# docker login -u mlplatformacr $CONTAINER_REGISTRY

docker build -t $DOCKER_IMAGE .
docker tag $DOCKER_IMAGE:latest $CONTAINER_REGISTRY/$DOCKER_IMAGE:latest
docker push $CONTAINER_REGISTRY/$DOCKER_IMAGE:latest
