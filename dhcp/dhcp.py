import os
import re
import subprocess
import ipaddress

# Função para capturar o IP da interface vmbr0
def get_ip_address(interface):
    try:
        result = subprocess.run(['ip', 'addr', 'show', interface], stdout=subprocess.PIPE, text=True)
        ip_match = re.search(r'inet\s+([\d.]+)', result.stdout)
        if ip_match:
            return ip_match.group(1)
        else:
            raise ValueError(f"Não foi possível capturar o IP da interface {interface}.")
    except Exception as e:
        print(f"Erro ao capturar o IP: {e}")
        return None

# Função para calcular a rede baseada no IP
def calculate_network(ip_address):
    ip_interface = ipaddress.ip_interface(f"{ip_address}/24")
    network = ip_interface.network
    return network

# Função para criar o arquivo dhcp.conf baseado na rede calculada
def create_dhcp_conf(network):
    # Calcula o início e o fim da faixa DHCP
    network_address = ipaddress.IPv4Network(network)
    dhcp_start = str(list(network_address.hosts())[200])
    dhcp_end = str(list(network_address.hosts())[220])
    gateway = str(list(network_address.hosts())[0])  # Supondo que o gateway seja o segundo IP da rede

    conf_content = f"""
interface=vmbr0                    # Interface de rede
dhcp-range={dhcp_start},{dhcp_end},12h  # Faixa de IPs e tempo de lease

# Define o gateway padrão
dhcp-option=3,{gateway}            # 3 = gateway, IP do gateway

# Define o DNS para os clientes
dhcp-option=6,8.8.8.8,1.1.1.1      # 6 = DNS server, pode definir mais de um

# Define a máscara de rede
dhcp-option=1,255.255.255.0        # 1 = subnet mask

port=0
"""
    try:
        # Salva o arquivo em /tmp
        with open('/tmp/dhcp.conf', 'w') as conf_file:
            conf_file.write(conf_content)
        print("Arquivo dhcp.conf criado com sucesso em /tmp.")
    except Exception as e:
        print(f"Erro ao criar o arquivo de configuração: {e}")

# Função para executar o dnsmasq
def start_dnsmasq():
    try:
        subprocess.run(['dnsmasq', '--no-daemon', '--conf-file=/tmp/dhcp.conf'])
    except Exception as e:
        print(f"Erro ao executar o dnsmasq: {e}")

if __name__ == "__main__":
    interface = 'vmbr0'
    ip_address = get_ip_address(interface)

    if ip_address:
        print(f"Endereço IP capturado na interface {interface}: {ip_address}")
        network = calculate_network(ip_address)
        print(f"Rede calculada: {network}")
        create_dhcp_conf(network)
        start_dnsmasq()
