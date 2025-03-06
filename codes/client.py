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
        while comprimento == False:
            com1.rx.clearBuffer()

            print("-------------------------")
            print("Tentando Handshake")
            print("-------------------------")

            load_hs = b'0'
            txBuffer = datagrama(load_hs,1,1,0,0,numero_server) #handshake client = 1, handshake server = 2, dados = 3, eop certo = 4, timeou = 5, erro = 6

            com1.sendData(txBuffer)
            print("Pacote de handshake enviado!")

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))
            time.sleep(0.5)


            print("Esperando resposta...")
            # Removido timeout_5s(com1)
            
            # Correção para aguardar resposta sem bloquear
            while com1.rx.getBufferLen() < 1:
                time.sleep(1)
                
            # Ler o que está disponível no buffer em vez de bloquear
            rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())

            if check_h0(rxBuffer,2): #check se o pacote é de handshake (2 pelo server)
                print("Handshake confirmado!")
                comprimento = True #sai do loop do handshake
                com1.rx.clearBuffer()
                time.sleep(0.5)
                clear_terminal()

            else:
                print("Handshake falhou!")
                time.sleep(0.5)
                com1.rx.clearBuffer()
                clear_terminal()

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