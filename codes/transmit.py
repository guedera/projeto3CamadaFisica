from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal

serialName = "/dev/ttyACM1"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        print("Enviando o byte de sacrifício")
        com1.sendData(b'0')
        print("Byte de sacrifício enviado!\n")
        time.sleep(0.2)

        com1.rx.clearBuffer()

        imageR = "codes/img/image.png"

        txBuffer = open(imageR, 'rb').read()

        #aqui dividiremos a imagem em pacotes!!

        imagem = bytearray(b'1') #exemplo, aqui vai o pacote!!!

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