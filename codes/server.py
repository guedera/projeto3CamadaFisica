from enlace import *
import time
import numpy as np
import os
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama
from certo import check_h0, certo

# IMPORTANTE: No servidor, use a porta correta!
serialName = "/dev/ttyACM1"  # <<< Ajuste conforme necessário no seu computador

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        
        # Limpa o buffer no início
        com1.rx.clearBuffer()
        
        print("-------------------------")
        print("Esperando byte de sacrifício...")
        print("-------------------------")
        
        # Aguarda o byte de sacrifício (não bloqueante)
        while com1.rx.getBufferLen() == 0:
            time.sleep(0.1)
            
        # Recebe o byte de sacrifício
        sacrifice_byte, _ = com1.getData(1)
        print("Byte de sacrifício recebido!")
        time.sleep(0.5)
        com1.rx.clearBuffer()
        
        print("-------------------------")
        print("Esperando handshake do client...")
        print("-------------------------")
        
        # File to save received data
        file_bytes = bytearray()
        
        # Handshake stage
        handshake_confirmed = False
        
        # Loop para aguardar handshake (sem timeout)
        while not handshake_confirmed:
            if com1.rx.getBufferLen() > 0:
                # Lê o que está disponível
                rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                
                # Debug
                print(f"Bytes recebidos: {nRx}, Conteúdo: {rxBuffer[:10]}...")
                
                if nRx > 0 and check_h0(rxBuffer, 1):  # Verifica se é handshake do cliente
                    print("Handshake recebido!")
                    
                    # Extrai informações do handshake
                    server_id = rxBuffer[5]
                    total_packets = rxBuffer[1]  # Total de pacotes informado no handshake
                    print(f"ID do servidor: {server_id}")
                    print(f"Total de pacotes: {total_packets}")
                    
                    # Responde com handshake (tipo 2)
                    handshake_response = datagrama(b'0', 0, 2, 0, 1, server_id)
                    com1.sendData(handshake_response)
                    print("Enviando resposta de handshake (tipo 2)")
                    
                    handshake_confirmed = True
                    time.sleep(0.5)
                    clear_terminal()
                else:
                    print(f"Recebido pacote inválido ou não é handshake")
                    com1.rx.clearBuffer()
            else:
                print("Aguardando dados...")
                time.sleep(0.1)
        
        # Data reception stage
        expected_packet = 1
        last_received = 0
        
        # Start receiving packets
        while last_received < total_packets:
            print(f"Esperando pacote {expected_packet}...")
            
            # Wait for data (sem timeout)
            data_received = False
            
            while not data_received:
                if com1.rx.getBufferLen() >= 12:  # Pelo menos o cabeçalho
                    # Ler o tamanho do header primeiro
                    rxBuffer, nRx = com1.getData(12)  # Header tem 12 bytes
                    
                    # Verificar se é pacote de dados (tipo 3)
                    if check_h0(rxBuffer, 3):
                        # Extrair informações do cabeçalho
                        packet_number = rxBuffer[4]  # h4: número do pacote
                        payload_size = rxBuffer[3]   # h3: tamanho do payload
                        
                        print(f"Recebendo pacote {packet_number}, payload: {payload_size} bytes")
                        
                        # Aguarda até ter bytes suficientes para o payload + EOP
                        while com1.rx.getBufferLen() < payload_size + 3:
                            time.sleep(0.01)
                            
                        # Agora lê o payload e o EOP
                        payload_eop, _ = com1.getData(payload_size + 3)  # payload + EOP (3 bytes)
                        
                        # Separar payload e EOP
                        payload = payload_eop[:-3]
                        eop = payload_eop[-3:]
                        
                        # Verificar integridade do pacote
                        error = False
                        error_message = ""
                        
                        # Verificar sequência
                        if packet_number != expected_packet:
                            error = True
                            error_message += f"Erro na sequência. Esperado: {expected_packet}, Recebido: {packet_number}\n"
                        
                        # Verificar tamanho do payload
                        if len(payload) != payload_size:
                            error = True
                            error_message += f"Erro no tamanho do payload. Esperado: {payload_size}, Recebido: {len(payload)}\n"
                        
                        # Verificar EOP
                        if eop != b'\xAA\xBB\xCC':
                            error = True
                            error_message += "EOP incorreto!\n"
                        
                        # Tratar erros ou sucesso
                        if error:
                            print(error_message)
                            # Envia mensagem de erro (tipo 6)
                            error_response = datagrama(b'0', expected_packet, 6, expected_packet, last_received, server_id)
                            com1.sendData(error_response)
                            print(f"Enviando resposta de erro (tipo 6) solicitando pacote {expected_packet}")
                        else:
                            # Adiciona payload aos dados do arquivo
                            file_bytes.extend(payload)
                            
                            # Atualiza contadores
                            last_received = packet_number
                            expected_packet = packet_number + 1
                            
                            # Envia mensagem de sucesso (tipo 4)
                            success_response = datagrama(b'0', packet_number, 4, 0, 1, server_id)
                            com1.sendData(success_response)
                            print(f"Enviando confirmação (tipo 4) para pacote {packet_number}")
                        
                        data_received = True
                    else:
                        print(f"Recebido pacote tipo {rxBuffer[0]} ao invés de dados")
                        com1.rx.clearBuffer()
                else:
                    time.sleep(0.01)
            
            # Limpa o buffer para o próximo pacote
            com1.rx.clearBuffer()
            time.sleep(0.2)
            clear_terminal()
        
        # Salvar o arquivo recebido
        print("Todos os pacotes recebidos com sucesso!")
        
        # Garante que o diretório existe
        img_dir = "img"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        # Salva a imagem
        with open(os.path.join(img_dir, "imagecopy.png"), "wb") as file:
            file.write(file_bytes)
        print("Imagem salva como 'img/imagecopy.png'")
        
        # Envia confirmação final
        final_response = datagrama(b'0', total_packets, 4, 0, 1, server_id)
        com1.sendData(final_response)
        print("Enviada confirmação final")
        
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

if __name__ == "__main__":
    main()