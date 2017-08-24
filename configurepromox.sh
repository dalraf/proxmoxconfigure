#/bin/bash
function perguntar() {
	read -p "$1 ?(y/n) "
	return 0
}

function confirmaexec() {
    if [ "AUTOEXEC" == "sim" ]
    then
        $1
    else
	    read -p "Confirma execucao de ==> $1 ? digite (a) para execucao automatica (y/n/a)"
        if [ "$REPLY" == "y" ]
        then
            $1
        elif [ "$REPLY" == "a" ]
        then
            AUTOEXEC="sim"
            $1
        fi
    fi
}

perguntar "Deseja configurar o servidor com ansible"
if [ "$REPLY" == "y" ] 
then
    apt-get -y install python-pip
    apt-get -y install python-dev
    apt-get -y install sshpass
    pip install ansible
    ansible-playbook --ask-vault-pass -i "localhost," installproxmox.yml
fi

perguntar "Deseja configurar a raid"
if [ "$REPLY" == "y" ] 
then
    perguntar "Qual tipo de raid (1 ou 10)"
    if [ "$REPLY" == "1" ]
    then
        confirmaexec "sgdisk -R=/dev/sda /dev/sdb"
        confirmaexec "dd if=/dev/sda1 /dev/sdb1"
        confirmaexec "dd if=/dev/sda2 /dev/sdb2"
        confirmaexec "mdadm --create -l1 -n2 /dev/md0 /dev/sdb3 missing"
        confirmaexec "pvcreate /dev/md0"
        confirmaexec "vgextend pve /dev/md0"
        confirmaexec "pvmove /dev/sda3 /dev/md0"
        confirmaexec "vgreduce /dev/sda3"
        confirmaexec "mdadm --add /dev/md0 /dev/sda3"
        confirmaexec "update-grub"
        confirmaexec "grub-install /dev/sda"
        confirmaexec "grub-install /dev/sdb"
    elif [ "$REPLY" == "10" ]
    then
        confirmaexec "sgdisk -R=/dev/sda /dev/sdb"
        confirmaexec "sgdisk -R=/dev/sda /dev/sdc"
        confirmaexec "sgdisk -R=/dev/sda /dev/sdd"
        confirmaexec "dd if=/dev/sda1 /dev/sdb1"
        confirmaexec "dd if=/dev/sda2 /dev/sdb2"
        confirmaexec "dd if=/dev/sda1 /dev/sdc1"
        confirmaexec "dd if=/dev/sda2 /dev/sdc2"
        confirmaexec "dd if=/dev/sda1 /dev/sdd1"
        confirmaexec "dd if=/dev/sda2 /dev/sdd2"       
        confirmaexec "mdadm --create -l10 -n2 /dev/md0 /dev/sdb3 /dev/sdc3 /dev/sdd3 missing"
        confirmaexec "pvcreate /dev/md0"
        confirmaexec "vgextend pve /dev/md0"
        confirmaexec "pvmove /dev/sda3 /dev/md0"
        confirmaexec "vgreduce /dev/sda3"
        confirmaexec "mdadm --add /dev/md0 /dev/sda3"
        confirmaexec "update-grub"
        confirmaexec "grub-install /dev/sda"
        confirmaexec "grub-install /dev/sdb"
    fi

fi


