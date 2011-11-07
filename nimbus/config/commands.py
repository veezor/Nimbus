#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command



from nimbus.shared import utils
from nimbus.config.models import Config
from nimbus.libs.commands import command
from nimbus.storages.models import Storage
from nimbus.computers.models import Computer
from nimbus.security.models import register_administrative_nimbus_models

from nimbus.libs.bacula import ( ReloadManager,
                                 ReloadManagerService,
                                 force_unlock_bacula_and_start)



@command("--create-database")
def create_database():
    u"""Cria a base de dados do nimbus"""
    call_command('syncdb',verbosity=0,interactive=False)
    if len(User.objects.all()) == 0:
        u = User(username = "admin",
                 is_superuser=True,
                 email = "suporte@veezor.com")
        u.set_password("admin")
        u.save()

        call_command('loaddata', settings.INITIALDATA_FILE)


        config = Config.get_instance()
        config.director_password = utils.random_password()
        config.save()

        storage = Storage.objects.get(id=1)
        storage.password =  utils.random_password()
        storage.save()

        computer = Computer.objects.get(id=1)
        computer.activate()

        register_administrative_nimbus_models()

        reload_manager = ReloadManager()
        reload_manager.force_reload()
    else:
        force_unlock_bacula_and_start()


@command("--start-reload-manager-service")
def reload_manager_service(self):
    u"""Inicia o serviço de reload das configurações do bacula"""
    service = ReloadManagerService()
    service.run()


