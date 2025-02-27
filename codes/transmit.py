from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama
from certo import certo, handshake

serialName = "/dev/ttyACM0"

def main():
    try:
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
            txBuffer = datagrama(load_hs,0,0,0,0) #Tipo 0 é handshake (3º argumento da função datagrama)

            com1.sendData(txBuffer)
            print("Pacote de handshake enviado!")

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))
            time.sleep(0.5)


            print("Esperando resposta...")
            rxBuffer = com1.getData(16) #16 bytes pois o payload é de 1 byte (pra função datagrama não dar erro)

            if handshake(rxBuffer,0): #check se o pacote é de handshake
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

        i = 0
        while i < len(bytes_partes):
            data = datagrama(bytes_partes[i],i,1,0,0)
            txBuffer = data
            com1.sendData(txBuffer)

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))

            print("Pacote {} enviado!".format(i))
            time.sleep(0.5)

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

        
        print("Imagem enviada!")
        time.sleep(0.5)

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