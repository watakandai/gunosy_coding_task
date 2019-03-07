#!/bin/sh

#################################
# Before start,                 #
# chmod 755 refresh_docker.sh   #
# then run ./refresh_docker.sh  #
#################################

#docker stop $(docker ps -q -a)
#docker rm $(docker ps -q -a)
docker-compose build 
docker-compose run webapp python manage.py migrate
