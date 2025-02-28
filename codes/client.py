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
            timeout_5s(com1)

            rxBuffer = com1.getData(16) #16 bytes pois o payload é de 1 byte (pra função datagrama não dar erro)

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

        i = 1
        while i < len(bytes_partes):
            data = datagrama(bytes_partes[i],i,3,0,0,numero_server)
            txBuffer = data
            com1.sendData(txBuffer)

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))

            print("Pacote {} enviado!".format(i))
            time.sleep(0.5)

            timeout_5s(com1)

            rxBuffer = com1.getData(16) #16 da funcao, arrumar depois a logica juntos. mas vai funfar

            if certo(rxBuffer,i):
                print("Pacote {} confirmado!".format(i))
                print("Iniciando envio do pŕoximo pacote...")
                i += 1
                com1.rx.clearBuffer()
                time.sleep(0.5)
                clear_terminal()

            else:
                print("Enviando o pacote {} novamente!".format(i))
                com1.rx.clearBuffer()
                time.sleep(0.5)
                clear_terminal()
        
        print("Confirmando que tudo foi enviado recebido no server corretamente!")
        timeout_5s(com1)
        rxBuffer = com1.rx.getData(16)

        if certo(rxBuffer,len(bytes_partes)):
            print("Pacote {} confirmado!".format(i))
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

def timeout_5s(com1):
    tempo_antes = time.time()
    while tempo_antes - time.time() < 5:
        if com1.rx.getBufferLen() == 16:
            break
        else:
            print("Time out")
            break
        
if __name__ == "__main__":
    main()