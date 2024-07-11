#!/bin/bash
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

# Check Docker Service
if docker -v &> /dev/null ; then
if ! (( $(ps -ef | grep -v grep | grep docker | wc -l) > 0 )) ; then
sudo service docker start > /dev/null 2>&1 ; sleep 2 ; fi ; fi

# Create Docker Image
if [[ -z $(docker image ls | grep kitsune) ]]; then
  sudo docker build -t joelgmsec/kitsune .
fi

# Main Function
sudo xhost +local: > /dev/null
sudo docker run -it --rm --net host -v /tmp:/tmp -v "$(pwd):/opt/Kitsune" joelgmsec/kitsune
