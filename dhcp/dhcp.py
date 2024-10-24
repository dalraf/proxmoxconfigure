import subprocess
import re
import ipaddress

# Função para capturar o gateway a partir da rota default
def get_gateway():
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'], stdout=subprocess.PIPE, text=True)
        # Captura o gateway da rota default
        gateway_match = re.search(r'default via ([\d.]+)', result.stdout)
        
        if gateway_match:
            gateway = gateway_match.group(1)
            return gateway
        else:
            raise ValueError("Não foi possível capturar o gateway.")
    except Exception as e:
        print(f"Erro ao capturar o gateway: {e}")
        return None

# Função para criar o arquivo dhcp.conf baseado no IP do gateway
def create_dhcp_conf(gateway):
    # Considera a máscara /24
    gateway_ip = ipaddress.IPv4Address(gateway)
    network = ipaddress.IPv4Network(f"{gateway_ip}/24", strict=False)

    dhcp_start = str(list(network.hosts())[200])  # Início da faixa DHCP
    dhcp_end = str(list(network.hosts())[220])    # Fim da faixa DHCP

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
    gateway = get_gateway()

    if gateway:
        print(f"Gateway capturado: {gateway}")
        create_dhcp_conf(gateway)
        start_dnsmasq()
