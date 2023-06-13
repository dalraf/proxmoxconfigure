import subprocess
import re
import sys
from config_backup_hd_externo import (
    lista_rsync_coopsef,
    password,
)


def run_interactive(command):
    print(f'Executando o comando  "{command}"')
    subprocess.call(command, shell=True)


def run_padrao(command):
    print(f'Executando o comando  "{command}"')
    subprocess.call(command, shell=True)


def run_hide(command):
    print(f'Executando o comando  "{command}"')
    saida = subprocess.check_output(command, shell=True).decode()
    return saida


def verify_device(lista_dispositivos):
    text_fstab = run_hide('cat /etc/fstab')
    text_raid = run_hide('cat /proc/mdstat')
    text_lvm = run_hide('pvdisplay')
    text_verify = text_fstab + text_raid + text_lvm
    for device in lista_dispositivos:
        device_head = device[1].replace('/dev/','')
        print(text_verify)
        print(device_head)
        if text_verify.find(device_head):
            del device
    return lista_dispositivos


def find_device():
    lista_dispositivos = run_hide("lshw -class disk -short").split("\n")
    lista_dispositivos = [
        i.strip().split(" ") for i in lista_dispositivos if re.search("sd", i)
    ]
    lista_dispositivos = [[j for j in i if j != ""] for i in lista_dispositivos]
    lista_dispositivos = verify_device(lista_dispositivos)
    return lista_dispositivos


def select_device(lista_dispositivos):
    if len(lista_dispositivos) > 0:
        print("Escolha o dispositivo")
        for index, var in enumerate(lista_dispositivos):
            print(index, ": ", " ".join(var[1:]))
        escolha = int(input(">>>>> "))
        return lista_dispositivos[escolha]
    else:
        print('Não foram encontrados dispositivos')
        sys.exit(1)

def verify_partition(dispositivo):
    vol_raw = run_hide("lsblk --output NAME -n -l " + dispositivo)
    vol_atual = [i for i in vol_raw.split("\n") if re.search(r"sd[a-z]1", i)]
    return "/dev/" + vol_atual[0]


def format_crypto(volume):
    resposta = input(f"Deseja formatar volume {volume} em modo crypto? (s/n):")
    if resposta == "s":
        command = f"echo {password} | cryptsetup -q luksFormat {volume}"
        run_interactive(command)


def mount_crypto(volume):
    resposta = input(f"Deseja montar volume {volume} em modo crypto? (s/n):")
    if resposta == "s":
        command = f"echo {password} | cryptsetup luksOpen {volume} backup "
        run_interactive(command)


def format_ext4():
    resposta = input(
        "Deseja formatar e montar o dispositivo virtual de backup ? (s/n):"
    )
    if resposta == "s":
        command = "mkfs.ext4 /dev/mapper/backup"
        run_interactive(command)
        command = "mount /dev/mapper/backup /opt/hd"
        run_interactive(command)


def rsync_copy():
    resposta = input("Deseja iniciar a copia do backup? (s/n):")
    if resposta == "s":
        print("Escolha a Origem:")
        for index, (l1, l2) in enumerate(lista_rsync_coopsef):
            print(index, ": ", l1)
        escolha = int(input(">>>>> "))
        origem_dir = lista_rsync_coopsef[escolha][1]
        command = "rm /var/hd_copy.log"
        try:
            run_padrao(command)
        except Exception as e:
            print("Arquivo de log não existe")
        command = f"screen -S backup_externo -d -m rsync -rtv --delete --log-file=/var/log/hd_copy.log  {origem_dir} /opt/hd"
        run_padrao(command)


def verify_backup():
    command = "tail /var/log/hd_copy.log"
    run_interactive(command)


def finalizar_copia():
    command = "umount /opt/hd"
    run_interactive(command)
    command = "cryptsetup luksClose backup"
    run_interactive(command)
    print("Backup finalizado")


while True:
    menu = ["Iniciar backup", "Verificar backup", "Desmontar HD", "Sair"]

    print("----------------------------------")
    print("Menu de opções:")
    for index, texto in enumerate(menu):
        print(index, ": ", texto)

    escolha = int(input(">>>>> "))

    if escolha == 0:
        lista_dispositivo = select_device(find_device())
        volume = verify_partition(lista_dispositivo[1])
        format_crypto(volume)
        mount_crypto(volume)
        format_ext4()
        rsync_copy()
    elif escolha == 1:
        verify_backup()
    elif escolha == 2:
        finalizar_copia()
    elif escolha == 3:
        sys.exit(0)
    else:
        print("Opção inválida")
