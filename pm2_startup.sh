#!/bin/bash
echo $ROOT_HYDRA_FOLDER
. $CURRENT_PY_VENV/bin/activate
$CURRENT_PY_VENV/bin/python -u $ROOT_HYDRA_FOLDER/hydra-server/run_server.py
