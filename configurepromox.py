#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import subprocess
import glob
import requests
isolist = [
    "https://nyifiles.pfsense.org/mirror/downloads/pfSense-CE-2.4.5-RELEASE-amd64.iso.gz",
    "https://mirrors.gigenet.com/OSDN//clonezilla/72478/clonezilla-live-20200302-eoan-amd64.iso",
    "https://plug-mirror.rcac.purdue.edu/osdn//storage/g/s/sy/systemrescuecd/releases/6.1.3/systemrescuecd-amd64-6.1.3.iso",
    "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"
    "https://ufpr.dl.sourceforge.net/project/xigmanas/XigmaNAS-12.1.0.4/12.1.0.4.7542/XigmaNAS-x64-LiveCD-12.1.0.4.7542.iso"

]

def Str(value):
    if isinstance(value, list):
        return " ".join(value)
    if isinstance(value, basestring):
        return value
    return str(value)


def Glob(value):
    ret = glob.glob(value)
    if (len(ret) < 1):
        ret = [value]
    return ret


def downloadwgetisos():
    os.chdir("/var/lib/vz/template/iso")
    for iso in isolist:
        subprocess.call(
            "wget -c " + iso, shell=True,)
    subprocess.call("gunzip " + Str(Glob("pfSense*.iso.gz")), shell=True)
    


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

autoexec = ""


def confirmaexec(texto):
    global autoexec

    if ("autoexec" == "sim"):
        subprocess.call([str(texto)], shell=True)
    else:
        resposta = input(
            "Confirma execucao de ==> $1 ? digite (a) para execucao automatica (y/n/a)")
        if (str(resposta) == "y"):
            subprocess.call([str(texto)], shell=True)
        elif (str(resposta) == "a"):
            autoexec = sim
            subprocess.call([str(texto)], shell=True)


def perguntar(texto):
    resposta = str(input(texto + " ?(y/n) "))
    return(resposta)


if (perguntar("Deseja configurar o servidor com ansible") == "y"):
    subprocess.call(["apt-get", "-y", "install", "build-essential",
                     "libssl-dev", "libffi-dev", "python-dev"], shell=True)
    subprocess.call(["apt-get", "-y", "install", "python-pip"], shell=True)
    #    pip install -U pip
    subprocess.call(["pip", "install", "Jinja2"], shell=True)
    subprocess.call(["pip", "install", "cryptography==2.0.3"], shell=True)
    subprocess.call(["pip", "install", "ansible==2.3.2.0"], shell=True)
    subprocess.call(["ansible-playbook", "--ask-vault-pass", "-i",
                     "localhost,", "--connection=local", "installproxmox.yml"], shell=True)

if (perguntar("Deseja configurar a raid") == "y"):
    raid = perguntar("Qual tipo de raid (1, 10 ou 5)")
    if (raid == "1"):
        confirmaexec("sgdisk -R=/dev/sdb /dev/sda")
        confirmaexec("dd if=/dev/sda1 of=/dev/sdb1")
        confirmaexec("dd if=/dev/sda2 of=/dev/sdb2")
        confirmaexec("mdadm --create -l1 -n2 /dev/md0 /dev/sdb3 missing")
        confirmaexec("pvcreate /dev/md0")
        confirmaexec("vgextend pve /dev/md0")
        confirmaexec("pvmove /dev/sda3 /dev/md0")
        confirmaexec("vgreduce pve /dev/sda3")
        confirmaexec("mdadm --add /dev/md0 /dev/sda3")
        confirmaexec("update-grub")
        confirmaexec("grub-install /dev/sda")
        confirmaexec("grub-install /dev/sdb")
    elif (raid == "10"):
        confirmaexec("sgdisk -R=/dev/sdb /dev/sda")
        confirmaexec("sgdisk -R=/dev/sdc /dev/sda")
        confirmaexec("sgdisk -R=/dev/sdd /dev/sda")
        confirmaexec("dd if=/dev/sda1 of=/dev/sdb1")
        confirmaexec("dd if=/dev/sda2 of=/dev/sdb2")
        confirmaexec("dd if=/dev/sda1 of=/dev/sdc1")
        confirmaexec("dd if=/dev/sda2 of=/dev/sdc2")
        confirmaexec("dd if=/dev/sda1 of=/dev/sdd1")
        confirmaexec("dd if=/dev/sda2 of=/dev/sdd2")
        confirmaexec(
            "mdadm --create -l10 -n4 /dev/md0 /dev/sdb3 /dev/sdc3 /dev/sdd3 missing")
        confirmaexec("pvcreate /dev/md0")
        confirmaexec("vgextend pve /dev/md0")
        confirmaexec("pvmove /dev/sda3 /dev/md0")
        confirmaexec("vgreduce pve /dev/sda3")
        confirmaexec("mdadm --add /dev/md0 /dev/sda3")
        confirmaexec("update-grub")
        confirmaexec("grub-install /dev/sda")
        confirmaexec("grub-install /dev/sdb")
        confirmaexec("grub-install /dev/sdc")
        confirmaexec("grub-install /dev/sdd")
    elif (raid == "5"):
        confirmaexec("sgdisk -R=/dev/sdb /dev/sda")
        confirmaexec("sgdisk -R=/dev/sdc /dev/sda")
        confirmaexec("dd if=/dev/sda1 of=/dev/sdb1")
        confirmaexec("dd if=/dev/sda2 of=/dev/sdb2")
        confirmaexec("dd if=/dev/sda1 of=/dev/sdc1")
        confirmaexec("dd if=/dev/sda2 of=/dev/sdc2")
        confirmaexec(
            "mdadm --create -l5 -n3 /dev/md0 /dev/sdb3 /dev/sdc3 missing")
        confirmaexec("pvcreate /dev/md0")
        confirmaexec("vgextend pve /dev/md0")
        confirmaexec("pvmove /dev/sda3 /dev/md0")
        confirmaexec("vgreduce pve /dev/sda3")
        confirmaexec("mdadm --add /dev/md0 /dev/sda3")
        confirmaexec("update-grub")
        confirmaexec("grub-install /dev/sda")
        confirmaexec("grub-install /dev/sdb")
        confirmaexec("grub-install /dev/sdc")

if (perguntar("Deseja baixa algumas isos padrão?") == "y"):
    downloadwgetisos()
    print("Download finalizado")

if (perguntar("Deseja baixa a imagem do zabbix?") == "y"):
    file_id = '1nSDoNYnx-9U6HZCXWBlPk601gJx_5yRB'
    destination = '/var/lib/vz/template/cache/zabbix.tar.gz'
    download_file_from_google_drive(file_id, destination)
    print("Download finalizado")

if (perguntar("Deseja baixa a imagem do pfsense?") == "y"):
    file_id = '1O67gPgLZCDOKI1jwdI7_UUfO62OX0WhE'
    destination = '/var/lib/vz/dump/vzdump-qemu-pfsense.vma.gz'
    download_file_from_google_drive(file_id, destination)
    print("Download finalizado")