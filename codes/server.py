from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from recebe_datagrama import *
import os


serialName = "/dev/ttyACM0"

def main():
    try:
        imageW = "/home/guedes/Documents/Faculdade/Camadas/projeto3CamadaFisica/codes/img/image.png"
        
        handshake = False
        numero_servidor = 8
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.clearBuffer()

        # Buffer para armazenar os bytes da imagem recebida
        image_buffer = bytearray()

        print("esperando 1 byte de sacrifício")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.5)

        print("Abriu a comunicação!")
        print("\n")
        print("Recepção iniciada!")
        print("\n")
        print("Recebendo o pacote!")

        # Aguardando handshake
        while not handshake:
            if com1.rx.getBufferLen() >= 16:
                head, nRx = com1.getData(12) # Ler o head primeiro
                nada = com1.getData(1) # Ler o byte de nada
                EoP, len_EoP = com1.getData(3)
                h0,h1,h2,h3,h4,h5,h6,h7,_,_,_,_ = interpreta_head(head)
                
                if h0 == 1 and h5 == numero_servidor: # Se for handshake e para este servidor
                    handshake = True
                    # Envia resposta de handshake
                    head_bytes = bytearray(head)
                    head_bytes[0] = 2 # Altera tipo para handshake server
                    pacote = bytes(head_bytes) + EoP
                    com1.sendData(pacote)
                    print("Handshake confirmado. Aguardando dados...")
                    
                    # Prepara para receber dados
                    contador = 1
                    n = 1  # Contador de pacotes esperados
                    total_pacotes = 0  # Será atualizado com o valor real do primeiro pacote
                    
        # Loop principal de recebimento de dados
        while True:
            if com1.rx.getBufferLen() >= 16:
                head, _ = com1.getData(12)  # Lê o cabeçalho
                h0,h1,h2,h3,h4,h5,h6,h7,_,_,_,_ = interpreta_head(head)
                
                if h0 == 3:  # Se for pacote de dados
                    payload, _ = com1.getData(h3)  # Lê o payload
                    EoP, _ = com1.getData(3)  # Lê o EoP
                    
                    if h1 > 0 and total_pacotes == 0:
                        total_pacotes = h1  # Atualiza o total de pacotes a receber
                    
                    print(f"Recebido pacote {h4} de {h1} pacotes")
                    
                    # Verifica se é o pacote esperado
                    if h4 == n:
                        # Adiciona o payload ao buffer da imagem
                        image_buffer.extend(payload)
                        
                        # Pacote correto, envia confirmação
                        head_bytes = bytearray(head)
                        head_bytes[0] = 4  # Tipo de confirmação positiva
                        head_bytes[7] = 1  # Sucesso = verdadeiro
                        pacote = bytes(head_bytes) + EoP
                        com1.sendData(pacote)
                        
                        n += 1  # Incrementa contador de pacotes esperados
                        print(f"Pacote {h4} confirmado. Esperando próximo pacote...")
                    else:
                        # Pacote errado, pede reenvio
                        head_bytes = bytearray(head)
                        head_bytes[0] = 6  # Tipo de erro
                        head_bytes[6] = n  # Solicita o pacote esperado
                        head_bytes[7] = 0  # Sucesso = falso
                        pacote = bytes(head_bytes) + EoP
                        com1.sendData(pacote)
                        
                        print(f"Pacote errado, esperava {n}, recebeu {h4}. Solicitando reenvio...")
                
                if h4 >= h1:  # Se recebeu o último pacote
                    print("Todos os pacotes recebidos. Comunicação finalizada.")
                    break
                    
            time.sleep(0.1)

        f = open(imageW, 'wb')
        f.write(image_buffer)

        f.close()

        # Salva a imagem recebida
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
