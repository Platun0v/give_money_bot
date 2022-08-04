#!/bin/bash

if [ -n "$1" ]
then
  echo "Updating to $1"
  version=$1
else
  echo "Updating to latest version"
  version="latest"
fi

dcfile="docker-compose.yml"
prev=$(grep image: $dcfile)
new="    image: ghcr.io/platun0v/give-money-bot:$version"
sed -i "s~$prev~$new~g" $dcfile

echo "Stopping all services."
docker-compose kill
echo "Downloading latest images of services."
docker-compose pull
echo "Images up to date. Starting all services."
docker-compose up -d
echo "Infrastructure started. Give it a moment to warm up."
