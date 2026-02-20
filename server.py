import socket
import json
from protocolo import Quadro, Pacote, Segmento, enviar_pela_rede_ruidosa

# Configurações de Rede
MEU_VIP = "SERVIDOR_PRIME"
MEU_MAC = "AA:BB:CC:DD:EE:FF"
IP_ROTEADOR = ("127.0.0.1", 8000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 9000))

print(f"--- Servidor {MEU_VIP} Online ---")

while True:
    data, addr = sock.recvfrom(4096)
    
    # FASE 4: ENLACE - Verificação de Integridade [cite: 50]
    quadro_dict, integro = Quadro.deserializar(data)
    
    if not integro:
        print("\033[91m[ENLACE] Erro de CRC detectado! Descartando quadro...\033[0m")
        continue

    pacote = quadro_dict['data']
    
    # FASE 3: REDE - Verificação de Endereço 
    if pacote['dst_vip'] != MEU_VIP:
        continue
        
    segmento = pacote['data']
    
    # FASE 2: TRANSPORTE - Processar Dados e enviar ACK [cite: 34]
    if not segmento['is_ack']:
        msg_app = segmento['payload']
        print(f"\033[92m[APP] {msg_app['sender']}: {msg_app['message']}\033[0m")
        
        # Gerar ACK
        ack_seg = Segmento(seq_num=segmento['seq_num'], is_ack=True, payload={})
        ack_pac = Pacote(src_vip=MEU_VIP, dst_vip=pacote['src_vip'], ttl=64, segmento_dict=ack_seg.to_dict())
        ack_quadro = Quadro(src_mac=MEU_MAC, dst_mac=quadro_dict['src_mac'], pacote_dict=ack_pac.to_dict())
        
        enviar_pela_rede_ruidosa(sock, ack_quadro.serializar(), IP_ROTEADOR)
        print(f"[TRANSPORTE] ACK {segmento['seq_num']} enviado.")