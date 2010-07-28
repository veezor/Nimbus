#!/bin/bash

# copiando setting.py
if [ ! -f django/backup_corporativo/settings.py ];
then
    echo "copiando settings.py"
    cp -a django/backup_corporativo/settings_sample.py django/backup_corporativo/settings.py;
fi

# sobrescrevendo PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/libs:$(pwd)/webservices/manager
