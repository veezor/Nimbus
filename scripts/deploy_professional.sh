#!/bin/bash

unset PYTHONPATH
source initenv.sh

cd nimbus
python deploy.py professional
cd ../../deploy_tmp/
chmod -R 0755 .

unset PYTHONPATH
./scripts/generate_deb.sh professional