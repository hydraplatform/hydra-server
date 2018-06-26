#!/bin/bash
echo $ROOT_HYDRA_FOLDER
. ~/venv3/bin/activate
~/venv3/bin/python -u $ROOT_HYDRA_FOLDER/hydra-server/run_server.py
