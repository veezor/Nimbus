#!/bin/bash

function makedir(){
  mkdir -p $1 2>> /dev/null;
}


source initenv.sh;

makedir "deb/var"
makedir "deb/etc/init.d"
makedir "deb/etc/nimbus"
makedir "deb/etc/apache2/sites-enabled"
makedir "deb/var/log/nimbus"
makedir "deb/var/nimbus/deps"

find deb -iname "*~" -exec rm {} \;

cd django
cp backup_corporativo/settings_executable.py backup_corporativo/settings.py;
python2.5 setup.py build_exe ;
cp -a binary ../deb/var/www;
cd ..;


cd webservices/manager;
python2.5 setup.py build_exe;
cp -a binary ../../deb/var/nimbusmanager;
cd ../..;


cp django/apacheconf/default deb/etc/apache2/sites-enabled/000-default
cp -a django/cron.daily deb/etc/
cp -a custom deb/var/nimbus
cp django/backup_corporativo/logging.conf deb/etc/nimbus
cp webservices/manager/nimbus_manager.conf deb/etc/nimbus
cp webservices/manager/init.d/nimbusmanager deb/etc/init.d

dpkg-deb -b deb nimbus.deb


rm -rf deb/var/www
rm -rf deb/var/nimbus/custom
rm -rf deb/var/nimbusmanager/
