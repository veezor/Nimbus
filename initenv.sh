#!/bin/bash

# copiando diretório custom
if [ ! -d django/backup_corporativo/bkp/custom ];
then
    echo "copiando diretório custom";
    cp -a custom django/backup_corporativo/bkp;
fi

# copiando setting.py
if [ ! -f django/backup_corporativo/settings.py ];
then
    echo "copiando settings.py"
    cp -a django/backup_corporativo/settings_sample.py django/backup_corporativo/settings.py;
fi

# sobrescrevendo PYTHONPATH
export PYTHONPATH=$(pwd)/libs
