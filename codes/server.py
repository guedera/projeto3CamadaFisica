from enlace import *
import time
import numpy as np
import os
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama
from certo import check_h0, certo


serialName = "/dev/ttyACM0"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        
        # Wait for handshake from client
        print("Esperando byte de sacrifício...")
        rxBuffer, nRx = com1.getData(1)
        time.sleep(0.5)
        com1.rx.clearBuffer()
        
        print("-------------------------")
        print("Esperando handshake do client...")
        print("-------------------------")
        
        # File to save received data
        file_bytes = bytearray()
        
        # Handshake stage
        handshake_confirmed = False
        while handshake_confirmed == False:
            timeout_5s(com1)
            
            if com1.rx.getBufferLen() > 0:
                rxBuffer, nRx = com1.getData(16) # Header + small payload + EOP
                
                if check_h0(rxBuffer, 1):  # Check if it's handshake from client
                    print("Handshake recebido!")
                    
                    # Check server ID from client request
                    server_id = rxBuffer[5]
                    print(f"ID do servidor recebido: {server_id}")
                    
                    # Respond with handshake (type 2)
                    handshake_response = datagrama(b'0', 0, 2, 0, 1, server_id)
                    com1.sendData(handshake_response)
                    print("Enviando resposta de handshake (tipo 2)")
                    
                    handshake_confirmed = True
                    time.sleep(0.5)
                    clear_terminal()
                else:
                    print(f"Recebido pacote tipo {rxBuffer[0]} ao invés de handshake")
                    com1.rx.clearBuffer()
            else:
                print("Nenhum dado recebido, esperando...")
                time.sleep(0.5)
        
        # Data reception stage
        expected_packet = 1
        last_received = 0
        total_packets = 0
        
        # Start receiving packets
        while True:
            print(f"Esperando pacote {expected_packet}...")
            
            # Wait for data with timeout
            timeout = not timeout_5s(com1)
            
            if timeout:
                print("Timeout! Nenhum dado recebido em 5 segundos.")
                # Send timeout message (type 5)
                timeout_message = datagrama(b'0', 0, 5, 0, 0, server_id)
                com1.sendData(timeout_message)
                break
            
            # Get header
            rxBuffer, nRx = com1.getData(15)
            
            # Check if it's data packet (type 3)
            if check_h0(rxBuffer, 3):
                # Extract information from header
                packet_number = rxBuffer[4]  # h4: packet number
                payload_size = rxBuffer[3]   # h3: payload size
                
                # Get payload and EOP
                payload = rxBuffer[12:-3]  # Payload starts after header
                eop = rxBuffer[-3:]        # Last 3 bytes should be EOP
                
                print(f"Pacote {packet_number} recebido. Tamanho do payload: {len(payload)}")
                
                # Verify packet integrity
                error = False
                error_message = ""
                
                # Check packet sequence
                if packet_number != expected_packet:
                    error = True
                    error_message += f"Erro na sequência. Esperado: {expected_packet}, Recebido: {packet_number}\n"
                
                # Check payload size
                if len(payload) != payload_size:
                    error = True
                    error_message += f"Erro no tamanho do payload. Esperado: {payload_size}, Recebido: {len(payload)}\n"
                
                # Check EOP
                if eop != b'\xAA\xBB\xCC':
                    error = True
                    error_message += "EOP incorreto!\n"
                
                # Handle errors or success
                if error:
                    print(error_message)
                    # Send error message (type 6)
                    error_response = datagrama(b'0', expected_packet, 6, expected_packet, last_received, server_id)
                    com1.sendData(error_response)
                    print(f"Enviando resposta de erro (tipo 6) solicitando pacote {expected_packet}")
                else:
                    # Add payload to file data
                    file_bytes.extend(payload)
                    
                    # Update counters
                    last_received = packet_number
                    expected_packet = packet_number + 1
                    
                    # Get total packets if this is first packet
                    if packet_number == 1:
                        total_packets = rxBuffer[1]  # h1: total packets
                        print(f"Total de pacotes: {total_packets}")
                    
                    # Send success message (type 4)
                    success_response = datagrama(b'0', packet_number, 4, 0, 1, server_id)
                    com1.sendData(success_response)
                    print(f"Enviando confirmação (tipo 4) para pacote {packet_number}")
                    
                    # Check if this was the last packet
                    if packet_number == total_packets:
                        print("Último pacote recebido!")
                        break
            else:
                print(f"Recebido pacote tipo {rxBuffer[0]} ao invés de dados")
            
            # Clear buffer for next packet
            com1.rx.clearBuffer()
            time.sleep(0.5)
            clear_terminal()
        
        # Save received file
        if last_received == total_packets:
            print("Todos os pacotes recebidos com sucesso!")
            
            # Certifica-se que o diretório img existe antes de salvar
            img_dir = "img"
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
                
            # Salva a imagem como "imagecopy.png" na pasta img
            with open(os.path.join(img_dir, "imagecopy.png"), "wb") as file:
                file.write(file_bytes)
            print("Imagem salva como 'img/imagecopy.png'")
            
            # Send final confirmation
            final_response = datagrama(b'0', total_packets, 4, 0, 1, server_id)
            com1.sendData(final_response)
        
        # End communication
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

def timeout_5s(com1):
    tempo_inicio = time.time()
    while time.time() - tempo_inicio < 5:
        if com1.rx.getBufferLen() > 0:
            return True
        time.sleep(0.1)
    return False

if __name__ == "__main__":
    main()