#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from pprint import pprint
import re

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

def main():
    lista_dispositivo = (select_device(find_device()))
    print(lista_dispositivo)

if __name__ == "__main__":
    main()
