#!/bin/sh

#################################
# Before start,                 #
# chmod 755 refresh_docker.sh   #
# then run ./refresh_docker.sh  #
#################################

docker rmi $(docker images -q)
docker build .
docker-compose build 
docker-compose run webapp python manage.py migrate
