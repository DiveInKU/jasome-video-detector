#!/usr/bin/env bash

image_name='jasome-video-detector'
container_name='jasome-video-container'

if ! [ "$(git log --pretty=%H ...refs/heads/master^ | head -n 1)" = "$(git ls-remote origin -h refs/heads/master | cut -f1)" ]; then
  # need pull and rebuild image
  git pull origin master
  docker build -t $image_name .
fi

if [ "$(docker ps -aq -f name=$container_name)" ]; then
  # cleanup
  docker rm $container_name
fi
# run your container
docker run -it -p 8000:8000 --name $container_name $image_name
