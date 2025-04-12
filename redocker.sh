#!/bin/bash

IMAGE_NAME=scratch-web-app

echo "Building new Docker image (if repo changed, is it pushed and CACHEBUST updated?)..."
echo

docker build -t $IMAGE_NAME .

echo
echo "Building new Docker container from image..."
echo

docker run -d -p 3306:3306 -p 5000:5000 -p 3000:3000 $IMAGE_NAME

echo
echo "Redocking complete!"
