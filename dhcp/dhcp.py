# -*- coding: utf-8 -*-
import subprocess
import re
import ipaddress

# Função para capturar o gateway a partir da rota default
def get_gateway():
    try:
        # Removido o parâmetro `text=True` e substituído por `universal_newlines=True`
        result = subprocess.run(['ip', 'route', 'show', 'default'], stdout=subprocess.PIPE, universal_newlines=True)
        
        # Captura o gateway da rota default
        gateway_match = re.search(r'default via ([\d.]+)', result.stdout)
        
        if gateway_match:
            gateway = gateway_match.group(1)
            return gateway
        else:
            raise ValueError("Não foi possível capturar o gateway.")
    except Exception as e:
        print("Erro ao capturar o gateway: {}".format(e))
        return None

# Função para criar o arquivo dhcp.conf baseado no IP do gateway
def create_dhcp_conf(gateway):
    # Considera a máscara /24
    gateway_ip = ipaddress.IPv4Address(gateway)
    network = ipaddress.IPv4Network("{}/24".format(gateway_ip), strict=False)
    
    # Gera a máscara de rede no formato decimal (ex: 255.255.255.0)
    netmask = network.netmask

    dhcp_start = str(list(network.hosts())[200])  # Início da faixa DHCP
    dhcp_end = str(list(network.hosts())[220])    # Fim da faixa DHCP

    conf_content = """
interface=vmbr0                    # Interface de rede
dhcp-range={dhcp_start},{dhcp_end},12h  # Faixa de IPs e tempo de lease

# Define o gateway padrão
dhcp-option=3,{gateway}            # 3 = gateway, IP do gateway

# Define o DNS para os clientes
dhcp-option=6,8.8.8.8,1.1.1.1      # 6 = DNS server, pode definir mais de um

# Define a máscara de rede
dhcp-option=1,{netmask}            # 1 = subnet mask

port=0
""".format(dhcp_start=dhcp_start, dhcp_end=dhcp_end, gateway=gateway, netmask=netmask)
    
    try:
        # Salva o arquivo em /tmp
        with open('/tmp/dhcp.conf', 'w') as conf_file:
            conf_file.write(conf_content)
        print("Arquivo dhcp.conf criado com sucesso em /tmp.")
    except Exception as e:
        print("Erro ao criar o arquivo de configuração: {}".format(e))

# Função para executar o dnsmasq
def start_dnsmasq():
    try:
        subprocess.run(['dnsmasq', '--no-daemon', '--conf-file=/tmp/dhcp.conf'])
    except Exception as e:
        print("Erro ao executar o dnsmasq: {}".format(e))

if __name__ == "__main__":
    gateway = get_gateway()

    if gateway:
        print("Gateway capturado: {}".format(gateway))
        create_dhcp_conf(gateway)
        start_dnsmasq()
