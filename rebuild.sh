#!/bin/bash

if [ "$1" = "hard" ]; then
    docker compose down
fi

docker compose up --build
