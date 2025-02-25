from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama
from certo import certo

serialName = "/dev/ttyACM0"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        print("Enviando o byte de sacrifício")
        com1.sendData(b'00')
        print("Byte de sacrifício enviado!\n")
        time.sleep(0.2)

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

            print("Pacote {} enviado!".format(i))
            time.sleep(0.5)

            rxBuffer = com1.getData(15)

            if certo(rxBuffer,i):
                print("Pacote {} confirmado!".format(i))
                i += 1

            else:
                print("Enviando o pacote {} novamente!".format(i))
                time.sleep(0.5)
                
        com1.sendData(np.asarray(txBuffer))
        
        print("Pacote enviado!")
        time.sleep(0.5)

        txSize = com1.tx.getStatus()
        print('enviou = {} bytes!' .format(txSize))
        time.sleep(.5)

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