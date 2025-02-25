from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal


serialName = "/dev/ttyACM0"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.clearBuffer()

        print("esperando 1 byte de sacrifício")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.5)

        print("Abriu a comunicação!")
        print("\n")
        print("Recepção iniciada!")
        print("\n")

        print("Recebendo o pacote!")
        rxBuffer, nRx = com1.getData(12) #12 pq ele tem q ler o head primeiro

        #ai recebe o resto

        #interpreta o resto e recebe outros ou não
       

        
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
