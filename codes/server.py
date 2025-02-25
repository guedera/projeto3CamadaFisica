from enlace import *
import time

from IEEEToFloat import ieee754_to_float
from floatToIEEE import float_to_ieee754

import numpy as np

serialName = "/dev/ttyACM0"

def main():

    soma = []
    floats = []

    try:
        print("Iniciou o main")

        com1 = enlace(serialName)
        com1.enable()
        com1.rx.clearBuffer()
        com1.rx.clearBuffer()

        print("esperando 1 byte de sacrifício")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.5)
       
        print("Abriu a comunicação!")
        print("\n")
        print("Recepção iniciada!")
        print("\n")

        #Recebe o byte que indica o comprimento total dos dados a receber em bytes
        lengthData, lengthReceived = com1.getData(1)

        if lengthData and lengthReceived == 1:

            totalDataLength = lengthData[0]
            print(f"Esperando receber {totalDataLength} bytes")

            #Recebe os dados conforme o comprimento especificado
            rxBuffer, nRx = com1.getData(totalDataLength)
            print(f"Recebeu {nRx} bytes")
            print("\n")

            if nRx == totalDataLength and totalDataLength % 4 == 0:
                #Processa cada grupo de 4 bytes como um float
                
                for i in range(0, nRx, 4):
                    float_value = ieee754_to_float(rxBuffer[i:i+4])
                    floats.append(float_value)

                for f in floats:
                    print("Valor float recebido:", f)
                    
            else:
                print("Número de bytes recebido é inadequado para a conversão esperada ou não é múltiplo de 4.")
        else:
            print("Falha ao receber o comprimento total dos dados.")

        soma.append(sum(floats))
        soma[0]=+ 20.0

        txBuffer = bytearray(float_to_ieee754(soma))

        com1.sendData(np.asarray(txBuffer))
    
        print("\n")
        print("\n")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

if __name__ == "__main__":
    main()
