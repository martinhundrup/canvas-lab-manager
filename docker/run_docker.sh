#!/bin/bash
sudo docker build -f docker/Dockerfile . -t canvas-lab-manager

sudo docker run -u=$(id -u $USER):$(id -g $USER) -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/app:/app  -v .:/docker --rm canvas-lab-manager


