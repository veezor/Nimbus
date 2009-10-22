#!/bin/bash

# copiando diretório custom
cp -a custom django/backup_corporativo/bkp

# copiando setting.py
cp -a django/backup_corporativo/settings_sample.py django/backup_corporativo/settings.py

# sobrescrevendo PYTHONPATH
export PYTHONPATH=$(pwd)/libs
