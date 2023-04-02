#!/bin/bash

set -e

if [ ! -f .env ]
then
    ## Copy the environment variables to .env and append the IP address of the host machine
    cp .env.example .env
    echo "" >> .env
    echo HOST=http://localhost:8888 >> .env
    ## This can be usful if you are running your apps inside docker containers
    # echo HOST=$(ifconfig | grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" | grep -v 127.0.0.1 | head -1 | awk '{ print $2 }') >> .env
    mkdir -p wp-content/plugins
    cd wp-content/plugins
    git clone --branch stable https://github.com/valu-digital/wp-graphql-offset-pagination.git
fi

if [ ! -d wp-content ]
then
    mkdir -p wp-content/plugins
    cd wp-content/plugins
    git clone --branch stable https://github.com/valu-digital/wp-graphql-offset-pagination.git
    cd ../../
fi
