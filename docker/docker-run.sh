#!/bin/bash

IMAGE_NAME='lpp-custom-application'
ARCH=$(dpkg --print-architecture)

if [ $# -eq 1 ]; then
    VERSION=$1
    docker run -d --name lpp checkpt/${IMAGE_NAME}:${VERSION}
else
    echo -e "Example: docker-run.sh <VERSION>"
fi
