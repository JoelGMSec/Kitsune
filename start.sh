#!/bin/bash
#=========================#
#  Kitsune by @JoelGMSec  #
#      darkbyte.net       #
#=========================#

# Check Docker Service
if docker -v &> /dev/null ; then
if ! (( $(sudo ps -ef | grep -v grep | grep docker | wc -l) > 0 )) ; then
sudo service docker start > /dev/null 2>&1 ; sleep 2 ; fi ; fi

# Create Docker Image
if [[ -z $(sudo docker image ls | grep kitsune) ]] ; then
sudo docker build -t joelgmsec/kitsune . ; fi

# Copy fonts to ~/.local/share/fonts/
mkdir -p ~/.local/share/fonts > /dev/null 2>&1
cp -rf ./themes/fonts/* ~/.local/share/fonts/

# Main Function
sudo xhost +local: > /dev/null
sudo docker run -it --rm --net host \
  -v /tmp:/tmp \
  -v "$HOME/.local/share/fonts":/root/.local/share/fonts/ \
  -v /usr/share/icons:/usr/share/icons \
  -v "$(pwd):/opt/Kitsune" \
  -e XFONT_PATH="$HOME/.local/share/fonts/" \
  joelgmsec/kitsune
