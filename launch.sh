#!/usr/bin/env bash

python -m venv env
source env/bin/activate
pip install -r requirements.txt
./bin/cpu-g
