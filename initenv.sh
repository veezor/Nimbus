#!/bin/bash

# copiando diretório custom
cp -a custom django/backup_corporativo/bkp

# sobrescrevendo PYTHONPATH
export PYTHONPATH=$(pwd)/libs
