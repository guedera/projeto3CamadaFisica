from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama
from certo import check_h0, certo

serialName = "/dev/ttyACM0"

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
        timeout_count = 0
        max_attempts = 5
        
        while comprimento == False and timeout_count < max_attempts:
            com1.rx.clearBuffer()

            print("-------------------------")
            print("Tentando Handshake (tentativa {})".format(timeout_count + 1))
            print("-------------------------")

            load_hs = b'0'
            # Enviar h1 como número total de pacotes no handshake
            bytes_imagem = open("codes/img/image.png", 'rb').read()
            bytes_partes = separa(bytes_imagem)
            total_pacotes = len(bytes_partes)
            
            txBuffer = datagrama(load_hs, 1, 1, 0, 0, numero_server.to_bytes(1, 'big')) 
            # Ajuste: primeiro byte é tipo (1), h1 deve ser total de pacotes
            txBuffer = bytearray(txBuffer)
            txBuffer[1] = total_pacotes  # Define h1 como total de pacotes
            txBuffer = bytes(txBuffer)

            com1.sendData(txBuffer)
            print("Pacote de handshake enviado!")

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))

            print("Esperando resposta... (timeout em 5s)")
            
            # Implementação de timeout
            start_time = time.time()
            timeout = 5  # 5 segundos de timeout
            
            got_response = False
            
            while (time.time() - start_time < timeout) and not got_response:
                if com1.rx.getBufferLen() > 0:
                    rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
                    got_response = True
                time.sleep(0.1)
                
            if got_response and check_h0(rxBuffer, 2):  # check se o pacote é de handshake (2 pelo server)
                print("Handshake confirmado!")
                comprimento = True  # sai do loop do handshake
                com1.rx.clearBuffer()
                time.sleep(0.5)
                clear_terminal()
            else:
                print("Handshake falhou ou timeout! Tentando novamente...")
                timeout_count += 1
                time.sleep(1)
                com1.rx.clearBuffer()
                clear_terminal()
        
        if timeout_count >= max_attempts:
            print("Número máximo de tentativas de handshake excedido. Encerrando...")
            com1.disable()
            return

        imageR = "codes/img/image.png"
        bytes_imagem = open(imageR, 'rb').read() #imagem em sequencia de bytes
        bytes_partes = separa(bytes_imagem) #separa a imagem em partes de no max 70 bytes e coloca numa lista

        # Correção: começar do índice 0 para enviar todos os pacotes
        i = 0
        while i < len(bytes_partes):
            # Número do pacote é i+1 (começa em 1, não em 0)
            data = datagrama(bytes_partes[i], i+1, 3, 0, 0, numero_server)
            txBuffer = data
            com1.sendData(txBuffer)

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))

            print("Pacote {} enviado!".format(i+1))  # Mostrar número do pacote iniciando em 1
            time.sleep(0.5)

            # Removido timeout_5s(com1)
            
            # Aguardar resposta sem bloquear
            while com1.rx.getBufferLen() < 1:
                time.sleep(1)
                
            # Ler o que está disponível
            rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())

            if certo(rxBuffer, i+1):  # Verificar pacote i+1
                print("Pacote {} confirmado!".format(i+1))
                print("Iniciando envio do próximo pacote...")
                i += 1
                com1.rx.clearBuffer()
                time.sleep(0.5)
                clear_terminal()

            else:
                print("Enviando o pacote {} novamente!".format(i+1))
                com1.rx.clearBuffer()
                time.sleep(0.5)
                clear_terminal()
        
        print("Confirmando que tudo foi enviado recebido no server corretamente!")
        # Removido timeout_5s(com1)
        
        # Aguardar resposta final
        while com1.rx.getBufferLen() < 1:
            time.sleep(1)
            
        rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())

        if certo(rxBuffer, len(bytes_partes)):
            print("Pacote {} confirmado!".format(len(bytes_partes)))
            print("Imagem enviada com sucesso!")
            time.sleep(0.5)
            clear_terminal()

        else:
            print("Erro na transmissão do pacote!")
            time.sleep(0.5)
            clear_terminal()
        
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

# Função de timeout removida

if __name__ == "__main__":
    main()