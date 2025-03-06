from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama
from certo import check_h0, certo

serialName = "/dev/ttyACM0"  # Ajuste para a porta correta no seu computador

def main():
    try:
        numero_server = 8
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        print("Enviando o byte de sacrifício")
        com1.sendData(b'00')
        print("Byte de sacrifício enviado!\n")
        time.sleep(0.5)

        com1.rx.clearBuffer()
        clear_terminal()

        #Handshake
        comprimento = False
        tentativas = 0
        max_tentativas = 3  # Número máximo de tentativas
        
        while comprimento == False and tentativas < max_tentativas:
            com1.rx.clearBuffer()
            tentativas += 1

            print("-------------------------")
            print(f"Tentando Handshake ({tentativas}/{max_tentativas})")
            print("-------------------------")

            load_hs = b'0'
            # Informar o total de pacotes já no handshake
            imageR = "codes/img/image.png"
            bytes_imagem = open(imageR, 'rb').read()
            bytes_partes = separa(bytes_imagem)
            total_pacotes = len(bytes_partes)
            
            # Handshake com total de pacotes incluído no h1
            txBuffer = datagrama(load_hs, total_pacotes, 1, 0, 0, numero_server)
            com1.sendData(txBuffer)
            print("Pacote de handshake enviado!")

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))
            time.sleep(0.5)

            print("Esperando resposta...")
            
            # Implementar timeout para a resposta
            start_time = time.time()
            response_received = False
            
            while time.time() - start_time < 5 and not response_received:  # 5 segundos de timeout
                if com1.rx.getBufferLen() > 0:
                    # Ler os bytes disponíveis
                    rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                    
                    if check_h0(rxBuffer, 2):  # Check se o pacote é de handshake (2 pelo server)
                        print("Handshake confirmado!")
                        comprimento = True  # Sai do loop do handshake
                        response_received = True
                        com1.rx.clearBuffer()
                        time.sleep(0.5)
                        clear_terminal()
                    else:
                        print(f"Recebido pacote tipo {rxBuffer[0]} ao invés de handshake")
                        com1.rx.clearBuffer()
                time.sleep(0.1)
            
            if not response_received:
                print("Timeout! Servidor não respondeu.")
                time.sleep(1)
                clear_terminal()

        if not comprimento:
            print("Handshake falhou após várias tentativas. Encerrando.")
            com1.disable()
            return

        # Agora enviamos os pacotes de dados
        i = 0  # Começamos do primeiro pacote (índice 0)
        while i < total_pacotes:
            # O número do pacote enviado começa em 1
            packet_number = i + 1
            data = datagrama(bytes_partes[i], packet_number, 3, 0, 0, numero_server)
            com1.sendData(data)

            print(f"Pacote {packet_number} enviado! Tamanho: {len(bytes_partes[i])} bytes")
            time.sleep(0.5)

            # Esperar confirmação com timeout
            start_time = time.time()
            response_received = False
            
            while time.time() - start_time < 5 and not response_received:
                if com1.rx.getBufferLen() > 0:
                    rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                    
                    if check_h0(rxBuffer, 4):  # Tipo 4 é confirmação
                        print(f"Pacote {packet_number} confirmado!")
                        print("Iniciando envio do próximo pacote...")
                        i += 1  # Avança para o próximo pacote
                        response_received = True
                    elif check_h0(rxBuffer, 6):  # Tipo 6 é erro
                        expected_packet = rxBuffer[6]  # h6: pacote solicitado
                        print(f"Erro! Servidor solicitou pacote {expected_packet}")
                        # Ajuste do contador para reenviar o pacote correto
                        i = expected_packet - 1
                        response_received = True
                    
                    com1.rx.clearBuffer()
                    time.sleep(0.5)
                    clear_terminal()
                else:
                    time.sleep(0.1)
            
            if not response_received:
                print("Timeout! Servidor não respondeu. Tentando novamente.")
                # Sem incrementar i, tentará enviar o mesmo pacote

        print("Todos os pacotes enviados. Verificando confirmação final...")
        
        # Esperar confirmação final
        start_time = time.time()
        final_confirmation = False
        
        while time.time() - start_time < 5 and not final_confirmation:
            if com1.rx.getBufferLen() > 0:
                rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                
                if check_h0(rxBuffer, 4) and rxBuffer[1] == total_pacotes:
                    print("Confirmação final recebida!")
                    print("Imagem enviada com sucesso!")
                    final_confirmation = True
                
                com1.rx.clearBuffer()
            time.sleep(0.1)
        
        if not final_confirmation:
            print("Não recebeu confirmação final.")
        
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