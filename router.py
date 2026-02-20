import socket
import json
from protocolo import Quadro

# Tabela de Roteamento Estática 
TABELA_ROTEAMENTO = {
    "SERVIDOR_PRIME": ("127.0.0.1", 9000),
    "HOST_A": ("127.0.0.1", 7000)
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 8000))

print("--- Roteador Mini-NET Ativo ---")

while True:
    data, addr = sock.recvfrom(4096)
    quadro_dict, integro = Quadro.deserializar(data)
    
    if integro:
        pacote = quadro_dict['data']
        destino_vip = pacote['dst_vip']
        
        # FASE 3: Lógica de Roteamento 
        if destino_vip in TABELA_ROTEAMENTO and pacote['ttl'] > 0:
            pacote['ttl'] -= 1 # Decrementa TTL 
            print(f"[REDE] Encaminhando para {destino_vip} (TTL: {pacote['ttl']})")
            sock.sendto(data, TABELA_ROTEAMENTO[destino_vip])