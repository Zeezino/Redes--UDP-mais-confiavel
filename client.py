import socket
import time
from protocolo import Quadro, Pacote, Segmento, enviar_pela_rede_ruidosa

MEU_VIP = "HOST_A"
MEU_MAC = "11:22:33:44:55:66"
IP_ROTEADOR = ("127.0.0.1", 8000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 7000))
sock.settimeout(2.0) # Timeout de 2 segundos [cite: 35]

seq_atual = 0

def enviar_mensagem(texto):
    global seq_atual
    # FASE 1: APLICAÇÃO (JSON) [cite: 24]
    payload = {"type": "chat", "sender": MEU_VIP, "message": texto}
    
    confirmado = False
    while not confirmado:
        # Encapsulamento: Transporte -> Rede -> Enlace [cite: 17]
        seg = Segmento(seq_num=seq_atual, is_ack=False, payload=payload)
        pac = Pacote(src_vip=MEU_VIP, dst_vip="SERVIDOR_PRIME", ttl=64, segmento_dict=seg.to_dict())
        quadro = Quadro(src_mac=MEU_MAC, dst_mac="AA:BB", pacote_dict=pac.to_dict())
        
        enviar_pela_rede_ruidosa(sock, quadro.serializar(), IP_ROTEADOR)
        print(f"\033[93m[TRANSPORTE] Enviando SEQ {seq_atual}...\033[0m")
        
        try:
            data, addr = sock.recvfrom(4096)
            q_ack, integro = Quadro.deserializar(data)
            
            if integro and q_ack['data']['data']['is_ack'] and q_ack['data']['data']['seq_num'] == seq_atual:
                print("\033[92m[TRANSPORTE] ACK recebido!\033[0m")
                confirmado = True
                seq_atual = 1 - seq_atual # Alterna entre 0 e 1 [cite: 36]
        except socket.timeout:
            print("\033[91m[TRANSPORTE] Timeout! Retransmitindo...\033[0m")

while True:
    msg = input("Mensagem: ")
    enviar_mensagem(msg)