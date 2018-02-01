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
    apt-get -y install build-essential libssl-dev libffi-dev python-dev
    apt-get -y install python-pip
    pip install -U pip
    pip install Jinja2
    pip install cryptography==2.0.3
    pip install ansible==2.3.2.0
    ansible-playbook --ask-vault-pass -i "localhost," installproxmox.yml
fi

perguntar "Deseja configurar a raid"
if [ "$REPLY" == "y" ] 
then
    perguntar "Qual tipo de raid (1 ou 10)"
    if [ "$REPLY" == "1" ]
    then
        confirmaexec "sgdisk -R=/dev/sdb /dev/sda"
        confirmaexec "dd if=/dev/sda1 of=/dev/sdb1"
        confirmaexec "dd if=/dev/sda2 of=/dev/sdb2"
        confirmaexec "mdadm --create -l1 -n2 /dev/md0 /dev/sdb3 missing"
        confirmaexec "pvcreate /dev/md0"
        confirmaexec "vgextend pve /dev/md0"
        confirmaexec "pvmove /dev/sda3 /dev/md0"
        confirmaexec "vgreduce pve /dev/sda3"
        confirmaexec "mdadm --add /dev/md0 /dev/sda3"
        confirmaexec "update-grub"
        confirmaexec "grub-install /dev/sda"
        confirmaexec "grub-install /dev/sdb"
    elif [ "$REPLY" == "10" ]
    then
        confirmaexec "sgdisk -R=/dev/sdb /dev/sda"
        confirmaexec "sgdisk -R=/dev/sdc /dev/sda"
        confirmaexec "sgdisk -R=/dev/sdd /dev/sda"
        confirmaexec "dd if=/dev/sda1 of=/dev/sdb1"
        confirmaexec "dd if=/dev/sda2 of=/dev/sdb2"
        confirmaexec "dd if=/dev/sda1 of=/dev/sdc1"
        confirmaexec "dd if=/dev/sda2 of=/dev/sdc2"
        confirmaexec "dd if=/dev/sda1 of=/dev/sdd1"
        confirmaexec "dd if=/dev/sda2 of=/dev/sdd2"       
        confirmaexec "mdadm --create -l10 -n4 /dev/md0 /dev/sdb3 /dev/sdc3 /dev/sdd3 missing"
        confirmaexec "pvcreate /dev/md0"
        confirmaexec "vgextend pve /dev/md0"
        confirmaexec "pvmove /dev/sda3 /dev/md0"
        confirmaexec "vgreduce pve /dev/sda3"
        confirmaexec "mdadm --add /dev/md0 /dev/sda3"
        confirmaexec "update-grub"
        confirmaexec "grub-install /dev/sda"
        confirmaexec "grub-install /dev/sdb"
	confirmaexec "grub-install /dev/sdc"
	confirmaexec "grub-install /dev/sdd"	
    fi

fi
perguntar "Deseja baixa algumas isos padrão?"
if [ "$REPLY" == "y" ]
then
    cd /var/lib/vz/template/iso
    wget -c https://nyifiles.pfsense.org/mirror/downloads/pfSense-CE-2.4.1-RELEASE-amd64.iso.gz
    gunzip pfSense-CE-2.3.4-RELEASE-amd64.iso.gz
    wget -c http://c3sl.dl.osdn.jp/clonezilla/67925/clonezilla-live-2.5.2-17-amd64.iso
    wget -c https://ufpr.dl.sourceforge.net/project/systemrescuecd/sysresccd-x86/5.0.3/systemrescuecd-x86-5.0.3.iso
    wget -c https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso
    wget -c https://ufpr.dl.sourceforge.net/project/nas4free/NAS4Free-11.1.0.4/11.1.0.4.5065/NAS4Free-x64-LiveCD-11.1.0.4.5065.iso
fi


