#!/bin/bash

project_name="eyesmedia-version-info-services"
cd /usr/services/eyesmedia/apps/"${project_name}"
if ! [ -f /usr/services/eyesmedia/apps/"${project_name}"/venv/bin/activate ];
then
  sudo -u eyesmedia -s
  echo 'installing virtual envirement'
  python3 -m venv venv
  echo 'installing requirements package'
  echo 'start project...'
  source venv/bin/activate
  pip3 install --upgrade pip
  pip3 install -r requirements.txt
  python3 start.py
else
  # need to check package version
  sudo -u eyesmedia -s
  source venv/bin/activate
  echo 'checking requirements package'
  pip3 install -r requirements.txt
  echo 'start project...'
  python3 start.py
fi
