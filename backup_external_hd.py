#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import re
import sys
from config import lista_rsync
import time

def run_wait(command):
    print('Aguardando 3 segundos', flush=True)
    time.sleep(3)
    print('Executando o comando  "%s"' % command)
    #subprocess.run(command)


def find_device():
    lista_dispositivos = (
        subprocess.check_output("lshw -class disk -short", shell=True).decode().split("\n")
    )
    lista_dispositivos = [i.strip().split(' ') for i in lista_dispositivos if re.search('sd', i)]
    lista_dispositivos = [[i[7],i[22],i[23]] for i in lista_dispositivos]
    return lista_dispositivos

def select_device(lista_dispositivos):
    print("Escolha o dispositivo")
    for index, (l1, l2, l3) in enumerate(lista_dispositivos):
        print(index, ": ", l1, l2, l3)
    escolha = int(input('>>>>> '))
    return lista_dispositivos[escolha]

def verify_partition(dispositivo):
    vol_raw = subprocess.check_output('lsblk --output NAME -n -l ' + dispositivo, shell=True).decode()
    vol_atual = [i for i in vol_raw.split('\n') if re.search(r'sd[a-z]1',i)]
    return '/dev/' + vol_atual[0]

def format_crypto(volume):
    resposta = input('Deseja formatar volume %s em modo crypto? (s/n):' % volume)
    if resposta == 's':
        command = ('cryptsetup luksFormat ' + volume)
        run_wait(command)
    else:
        sys.exit(1)

def mount_crypto(volume):
    resposta = input('Deseja montar volume %s em modo crypto? (s/n):' % volume)
    if resposta == 's':
        command = ('cryptsetup luksOpen %s backup ' % volume)
        run_wait(command)
    else:
        sys.exit(1)

def format_ext4():
    resposta = input('Deseja formatar e montar o dispositivo virtual de backup ? (s/n):')
    if resposta == 's':
        command = ('mkfs.ext4 /dev/mapper/backup')
        run_wait(command)
        command = ('mount /dev/mapper/backup /opt/hd')
        run_wait(command)
    else:
        sys.exit(1)

def rsync_copy():
    resposta = input('Deseja iniciar a copia do backup? (s/n):')
    if resposta == 's':
        print('Escolha a Origem:')
        for index, (l1, l2) in enumerate(lista_rsync):
            print(index, ": ", l1)
        escolha = int(input('>>>>> '))
        origem_dir = lista_rsync[escolha][1]
        command = 'screen -S backup_externo -dm "rsync -rtv --delete %s /opt/hd"' % origem_dir
        run_wait(command)

    else:
        sys.exit(1)

def finalizar_copia():
    command = ('umount /opt/hd')
    run_wait(command)
    command = ('cryptsetup luksClose backup')
    run_wait(command)
    print('Backup finalizado')


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            lista_dispositivo = (select_device(find_device()))
            volume = verify_partition(lista_dispositivo[0])
            format_crypto(volume)
            mount_crypto(volume)
            format_ext4()
            rsync_copy()
        elif sys.argv[1] == 'stop':
            finalizar_copia()
    else:
        print('Use:\nbackup_external_hd.py start\nbackup_external_hd.py stop')

if __name__ == "__main__":
    main()
