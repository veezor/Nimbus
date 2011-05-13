#################################################################################
# Script para restaurar o banco mysql do Nimbus ao estado inicial de instalacao #
#                                                                               #
# Caso seu banco tenha senha adicione o parametro "-p" aos comandos:            #
#     mysql                                                                     #
#     mysqldump                                                                 #
#################################################################################


UNIX_TIME=$(date +"%s")

echo "###########################"
echo "# Fazendo backup do banco #"
echo "###########################"

mysqldump -uroot -pmysqladm -a -c --add-drop-table nimbus > nimbus_bkp_$UNIX_TIME.sql

echo "#################################################"
echo "# Backup feito em nimbus_bkp_"$UNIX_TIME".sql     #"
echo "# Para restaurar use:                           #"
echo "# mysql -D nimbus < nimbus_bkp_"$UNIX_TIME".sql   #"
echo "#################################################"

echo "#########################"
echo "# Recriando banco vazio #"
echo "#########################"

mysql -uroot -pmysqladm -e "drop database nimbus; create database nimbus;"
# echo "Digite a senha do mysql"
# mysql -pmysqladm -e "drop database nimbus; create database nimbus;"

echo "##################################"
echo "# Recriando estrutura de tabelas #"
echo "##################################"

python manage.py syncdb
python manage.py migrate

echo "#######################################"
echo "# Importando dados iniciais do Nimbus #"
echo "#######################################"

python manage.py loaddata ../deb/var/nimbus/initial_data.json
