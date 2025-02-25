from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from separa import separa
from datagramas import datagrama

serialName = "/dev/ttyACM1"

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

        imageR = "codes/img/image.png"

        bytes_imagem = open(imageR, 'rb').read()

        bytes_partes = separa(bytes_imagem)

        for i in range(len(bytes_partes)):
            data = datagrama(bytes_partes[i],i,1,0,0)
            txBuffer = data
            com1.sendData(txBuffer)
            print("Pacote {} enviado!".format(i))
            time.sleep(0.5)
            #agora tenho que confirmar que o server recebeu certo
            



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