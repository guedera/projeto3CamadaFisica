from enlace import *
import time
from autolimpa import clear_terminal

serialName = "/dev/ttyACM0"

def parse_head(head_bytes):
    """
    Interpreta os 12 bytes do cabeçalho e retorna um dicionário com os campos.
    Estrutura:
      h0: Tipo da mensagem
      h1, h2: (valores duplicados do tipo)
      h3: Tamanho do payload
      h4: Número do pacote
      h5: Em handshake, representa o ID do servidor; em dados, pode ser o tamanho do payload
      h6: Campo de erro
      h7: Indicador de sucesso (por exemplo, 1 para confirmação)
      h8, h9, h10, h11: Campos livres
    """
    if len(head_bytes) != 12:
        raise ValueError("Cabeçalho inválido: tamanho diferente de 12 bytes.")
    return {
        "h0": head_bytes[0],
        "h1": head_bytes[1],
        "h2": head_bytes[2],
        "h3": head_bytes[3],
        "h4": head_bytes[4],
        "h5": head_bytes[5],
        "h6": head_bytes[6],
        "h7": head_bytes[7],
        "h8": head_bytes[8],
        "h9": head_bytes[9],
        "h10": head_bytes[10],
        "h11": head_bytes[11],
    }

def check_eop(eop_bytes):
    """Verifica se os 3 bytes do EoP correspondem a b'\xAA\xBB\xCC'."""
    return eop_bytes == b'\xAA\xBB\xCC'

def build_datagram(payload: bytes, n_pacote: int, tipo: int, erro: int, sucesso: int, id: int) -> bytes:
    """
    Constrói o datagrama conforme especificado:
      - HEAD: 12 bytes
      - PAYLOAD: tamanho variável
      - EoP: 3 bytes fixos (b'\xAA\xBB\xCC')
      
    Para os tipos 1, 2, 4, 5 e 6, h5 recebe o valor do ID.
    Para o tipo 3 (dados), h5 recebe o tamanho do payload.
    """
    h0 = tipo.to_bytes(1, 'big')
    h1 = tipo.to_bytes(1, 'big')
    h2 = tipo.to_bytes(1, 'big')
    h3 = len(payload).to_bytes(1, 'big')
    h4 = n_pacote.to_bytes(1, 'big')
    if tipo in [1, 2, 4, 5, 6]:
        h5 = id.to_bytes(1, 'big')
    elif tipo == 3:
        h5 = len(payload).to_bytes(1, 'big')
    else:
        h5 = (0).to_bytes(1, 'big')
    h6 = erro.to_bytes(1, 'big')
    h7 = sucesso.to_bytes(1, 'big')
    h8 = b'0'
    h9 = b'0'
    h10 = b'0'
    h11 = b'0'
    EoP = b'\xAA\xBB\xCC'
    return h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9 + h10 + h11 + payload + EoP

def main():
    try:
        server_id = 8
        timeout_duration = 5  # segundos para considerar fim da transmissão
        print("Servidor iniciado!")
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.clearBuffer()

        # Sincronização: aguarda o byte de sacrifício
        print("Esperando byte de sacrifício...")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.5)

        # Handshake: aguarda pacote de handshake do cliente (16 bytes)
        print("Aguardando handshake do cliente...")
        handshake_received = False
        while not handshake_received:
            if com1.rx.getBufferLen() >= 16:
                head_bytes, _ = com1.getData(12)
                payload, _    = com1.getData(1)
                eop, _        = com1.getData(3)
                
                if not check_eop(eop):
                    print("Handshake recebido com EoP inválido. Ignorando pacote...")
                    continue

                head = parse_head(head_bytes)
                # Verifica se é handshake (tipo 1) e se h5 equivale ao ID do servidor
                if head["h0"] == 1 and head["h5"] == server_id:
                    print("Handshake recebido corretamente!")
                    response = build_datagram(payload, 1, 2, 0, 0, server_id)
                    print(response)
                    com1.sendData(response)
                    handshake_received = True
                else:
                    print("Pacote de handshake inválido ou não destinado a este servidor.")
            else:
                time.sleep(0.1)

        # Recepção dos pacotes de dados
        print("Iniciando recepção dos pacotes de dados...")
        expected_packet = 1
        file_buffer = b''
        last_packet_time = time.time()
        
        while True:
            if com1.rx.getBufferLen() >= 12:
                head_bytes, _ = com1.getData(12)
                head = parse_head(head_bytes)
                
                # Se não for pacote de dados (tipo 3), descarta-o
                if head["h0"] != 3:
                    print(f"Pacote com tipo {head['h0']} recebido; esperado tipo 3. Descartando...")
                    payload_len = head["h3"]
                    _ = com1.getData(payload_len)
                    _ = com1.getData(3)
                    continue

                payload_len = head["h3"]
                packet_number = head["h4"]

                payload, _ = com1.getData(payload_len)
                eop, _ = com1.getData(3)
                
                if not check_eop(eop):
                    print(f"Pacote {packet_number}: EoP inválido. Solicitando reenvio.")
                    error_packet = build_datagram(b'', expected_packet, 6, 0, 0, 0)
                    com1.sendData(error_packet)
                    continue
                
                if packet_number != expected_packet:
                    print(f"Pacote fora de ordem: esperado {expected_packet}, recebido {packet_number}. Solicitando reenvio.")
                    error_packet = build_datagram(b'', expected_packet, 6, 0, 0, 0)
                    com1.sendData(error_packet)
                    continue
                
                file_buffer += payload
                print(f"Pacote {packet_number} recebido com sucesso.")
                confirmation = build_datagram(b'', packet_number, 4, 0, 1, 0)
                com1.sendData(confirmation)
                expected_packet += 1
                last_packet_time = time.time()
            else:
                if time.time() - last_packet_time > timeout_duration:
                    print("Timeout na recepção. Encerrando transferência.")
                    break
                time.sleep(0.1)
        
        # Salva o arquivo recebido
        with open("imagem_recebida.png", "wb") as f:
            f.write(file_buffer)
        print("Arquivo recebido e salvo como 'imagem_recebida.png'.")
        
        com1.disable()
        
    except Exception as e:
        print("Erro:", e)
        com1.disable()

if __name__ == "__main__":
    clear_terminal()
    main()
