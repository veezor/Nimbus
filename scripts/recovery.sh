
config_network () {
    while [ -z $NETOK ]; do
        CURRENTIP=$(ip addr show eth0 | grep inet | grep -v inet6 | grep -v 127.0.0.1 | head -n1 | awk '{print $2}' | cut -d/ -f1)
        IP=$(dialog --stdout --title 'Configuracao de rede' --inputbox "Endereco IP Atual:\n\n$CURRENTIP\n\nDigite um novo endereco IP ou deixe em branco para manter o atual" 0 0)
        if [ -z $IP ]; then
            NEWIP=$CURRENTIP
        else
            NEWIP=$IP
        fi
        CURRENTMASK=$(ifconfig eth0 | grep Mask | awk '{print $4}' | cut -d: -f2)
        MASK=$(dialog --stdout --title 'Configuracao de rede' --inputbox "Mascara de rede Atual:\n\n$CURRENTMASK\n\nDigite uma nova mascara ou deixe em branco para manter a atual" 0 0)
        if [ -z $MASK ]; then
            NEWMASK=$CURRENTMASK
        else
            NEWMASK=$MASK
        fi
        CURRENTGATEWAY=$(ip route show 0.0.0.0/0 dev eth0 | cut -d\\ -f3 | awk '{print $3}')
        GATEWAY=$(dialog --stdout --title 'Configuracao de rede' --inputbox "Gateway de rede Atual:\n\n$CURRENTGATEWAY\n\nDigite um novo gateway ou deixe em branco para manter a atual" 0 0)
        if [ -z $GATEWAY ]; then
            NEWGATEWAY=$CURRENTGATEWAY
        else
            NEWGATEWAY=$GATEWAY
        fi
        CURRENTDNS=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
        DNS=$(dialog --stdout --title 'Configuracao de rede' --inputbox "Servidores DNS atuais:\n\n$CURRENTDNS\n\nDigite os novos servidores DNS, separados por espaco, ou deixe em branco para manter os atuais" 0 0)
        if [ -z $DNS ]; then
            NEWDNS=$CURRENTDNS
        else
            NEWDNS=$DNS
        fi
        dialog --title 'Configuracao de rede' --yesno "Deseja aplicas as seguintes configuracoes?\n\nIP: $NEWIP\nMascara: $NEWMASK\nGateway: $NEWGATEWAY\nServidores DNS: $NEWDNS" 0 0
        if [ $? = 0 ]; then
        	NETOK=true
        fi
    done
    ## CONFIGURA A REDE AQUI
cat << EOF > /etc/network/interfaces
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto eth0
iface eth0 inet static
	address $NEWIP
	netmask $NEWMASK
	gateway $NEWGATEWAY
	# dns-* options are implemented by the resolvconf package, if installed
	dns-nameservers $NEWDNS
	dns-search localdomain
EOF
    echo > /etc/resolv.conf
    for dns in $NEWDNS
    do
        echo "nameserver $dns" >> /etc/resolv.conf
    done
    /etc/init.d/networking restart &>> recovery.log
}

config_auth () {
    while [ -z $DONE ]; do
        OFFSITEUSER=$(dialog --stdout --title 'Configuracao do backup Offsite' --inputbox "Digite o nome do usuario do Offsite de onde sera restaurado o backup" 0 0)
        OFFSITEPASS=$(dialog --stdout --title 'Configuracao do backup Offsite' --passwordbox "Digite a senha do usuario do Offsite de onde sera restaurado o backup" 0 0)
        dialog --title 'Configuracao do backup Offsite' --msgbox 'Tentaremos obter suas configurações de offsite agora. Isso pode levar alguns segundos' 0 0
        ERROR=$(/var/www/nimbus --offsite-simple-config $OFFSITEUSER $OFFSITEPASS 2>>recovery.err)
        if [ $? = 0 ]; then
            dialog --title 'Configuracao do backup Offsite' --msgbox 'Configuração do Offsite concluída!' 0 0
            DONE=true
        else
            AUTHERROR=$(echo $ERROR | grep "Username or password error")
            if [ -z $AUTHERROR ]; then
                dialog --title 'Configuracao do backup Offsite' --msgbox "Não foi possivel conectar-se ao servidor. Por favor verifique suas configuracoes de rede." 0 0
                unset NETOK
                config_network
            else
                dialog --title 'Configuracao do backup Offsite' --msgbox "Erro na autenticacao. Usuario ou senha invalidos." 0 0
            fi
        fi
    done
}


dialog --title 'Disaster Recovery' --yesno 'A seguir iremos restaurar o servidor Nimbus baseado nos backups guardados Offsite. Deseja continuar?' 0 0
if [ $? = 1 ]; then
	exit 0
fi
config_network
config_auth

dialog --title 'Disaster Recovery' --yesno 'Iremos agora restaurar todos os dados deste Nimbus baseado na copia Offsite.\n\nDeseja continuar?' 0 0
if [ $? = 1 ]; then
	exit 0
fi

while true; do
    su - nimbus -c '/var/www/nimbus --recovery-nimbus'
    if [ $? = 0 ]; then
        dialog --title 'Configuracao do backup Offsite' --msgbox "A configuração foi finalizada.\n\nO servidor será reiniciado agora." 0 0
        reboot
        exit 0
    else
        dialog --title 'Configuracao do backup Offsite' --msgbox "Houveram problemas na restauração. Será feita uma nova tentativa de recuperação agora" 0 0    
    fi
done