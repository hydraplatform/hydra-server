#!/bin/bash
echo $ROOT_HYDRA_FOLDER
. ~/VirtualEnvs/venv3/bin/activate
~/VirtualEnvs/venv3/bin/python -u $ROOT_HYDRA_FOLDER/hydra-server/run_server.py
