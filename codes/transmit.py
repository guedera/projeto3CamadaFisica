from enlace import *

import time

import numpy as np

from floatToIEEE import float_to_ieee754

from IEEEToFloat import ieee754_to_float

import os

serialName = "/dev/ttyACM1"

lista = [1.3424, 54.45544, 200.002, 14.545454, 1.2323242435332, 1.346575688, 2.83492]
soma_lista = sum(lista)

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        print("Enviando o byte de sacrifício")
        com1.sendData(b'0')
        print("Byte de sacrifício enviado!\n")
        time.sleep(.2)

        com1.rx.clearBuffer()

        print("Vou mandar quantos números serão enviados!")
        txBuffer = bytearray([len(lista)*4])
        print("Estou enviando {} números flutuantes!\n" .format(len(lista)*4))
        com1.sendData(np.asarray(txBuffer))
        
        print("Enviado!")
        time.sleep(2)

        print("Abriu a comunicação! Vou enviar a lista de Floats!\n")
        
        # Converte a lista de floats para o formato IEEE 754
        txBuffer = bytearray(float_to_ieee754(lista))
        
        print("Meu array de bytes tem tamanho {}\n" .format(len(txBuffer)))
        
        com1.sendData(np.asarray(txBuffer))
        print("Enviado!")
        time.sleep(2)

        txSize = com1.tx.getStatus()
        print('enviou = {} bytes!' .format(txSize))
        time.sleep(2)

        print("Esperando a soma!")
        tempo_antes = time.time()
        time.sleep(5)
        print("tempo atual começou a contar!")

        while tempo_antes - time.time() < 5:
            if com1.rx.getBufferLen() == 4:
                break
            else:
                print("Time out")
                break


            
        rxBuffer, nRx = com1.getData(4)


        print("Recebeu a soma!")
        print(rxBuffer)
        retorno = ieee754_to_float(rxBuffer)
        print("O resultado da soma é: ", retorno)
        time.sleep(2)

        if (soma_lista - retorno)< 0.1:
            print("Soma correta!")
            print(f" O valor recebido pelo server é : {retorno} e a soma da lista é {soma_lista}")

        else:
            print("Soma errada!")
            print(f" O valor recebido pelo server é : {retorno} e a soma da lista é {soma_lista}")
            print(f"Com uma diferença de {(soma_lista - retorno)}")
        time.sleep(2)

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