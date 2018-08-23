#!/bin/bash
source activate venv
export OAUTH_CALLBACK_URL=$(cat .callbackURL)
export OAUTH_CLIENT_SECRET=$(cat .clientSecret)
export OAUTH_CLIENT_ID=$(cat .clientID)
export DOCKER_NOTEBOOK_IMAGE="am2434/widap:latest"
jupyterhub -f jupyter_config.py --log-level=DEBUG
