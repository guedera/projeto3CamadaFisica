from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from recebe_datagrama import *
import os


serialName = "/dev/ttyACM1"

def main():
    try:
        imageW = "/home/guedera/Documents/Aulas/Camadas/projeto3CamadaFisica/codes/img/imagemcopia.png"  # Changed filename to match requirement
        
        handshake = False
        numero_servidor = 8
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.clearBuffer()

        # Buffer para armazenar os bytes da imagem recebida
        image_buffer = bytearray()
        total_pacotes = 0  # Inicializa total de pacotes

        print("esperando 1 byte de sacrifício")
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.5)
        
        print("Abriu a comunicação!")
        print("\n")
        print("Recepção iniciada!")
        print("\n")
        print("Recebendo o pacote!")

        # Configuração de timeout
        timeout_handshake = 20  # 20 segundos para handshake
        timeout_dados = 10      # 10 segundos para receber dados
        
        # Aguardando handshake com timeout
        start_handshake_time = time.time()
        
        while not handshake and (time.time() - start_handshake_time) < timeout_handshake:
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
                    n = 1  # Contador de pacotes esperados
            
            # Evita consumo excessivo de CPU
            time.sleep(0.1)
                    
        # Se não recebeu handshake no período definido, encerra o programa
        if not handshake:
            print(f"Timeout de handshake após {timeout_handshake} segundos. Encerrando o programa.")
            com1.disable()
            return
        
        # Loop principal de recebimento de dados com timeout
        last_packet_time = time.time()
        
        while True:
            # Verifica se houve timeout na comunicação
            if (time.time() - last_packet_time) > timeout_dados:
                print(f"Timeout após {timeout_dados} segundos sem receber dados. Encerrando o programa.")
                break
                
            if com1.rx.getBufferLen() >= 16:
                # Atualiza o tempo do último pacote recebido
                last_packet_time = time.time()
                
                head, _ = com1.getData(12)  # Lê o cabeçalho
                h0,h1,h2,h3,h4,h5,h6,h7,_,_,_,_ = interpreta_head(head)
                
                # Verifica se recebeu um pacote de timeout do cliente
                if h0 == 5:  # Tipo de pacote = timeout
                    print(f"Cliente reportou timeout para pacote {h4}. Finalizando comunicação.")
                    break
                
                if h0 == 3:  # Se for pacote de dados
                    payload, _ = com1.getData(h5)  # Lê o payload (tamanho está em h5 agora)
                    EoP, _ = com1.getData(3)  # Lê o EoP
                    
                    # CORREÇÃO: Usar h3 para determinar o número total de pacotes
                    if total_pacotes == 0:
                        total_pacotes = h3  # Atualiza o total de pacotes a receber
                        print(f"Total de pacotes a receber: {total_pacotes}")
                    
                    print(f"Recebido pacote {h4} de {total_pacotes} pacotes")
                    
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
                
                # CORREÇÃO: Verifica se recebemos todos os pacotes esperados
                if n > total_pacotes and total_pacotes > 0:  
                    print("Todos os pacotes recebidos. Enviando confirmação final...")
                    time.sleep(2)
                    # Envia confirmação final após receber todos os pacotes
                    head_bytes = bytearray(head)
                    head_bytes[0] = 4  # Tipo de confirmação positiva
                    head_bytes[4] = total_pacotes  # Número do último pacote (total)
                    head_bytes[7] = 1  # Sucesso = verdadeiro
                    pacote = bytes(head_bytes) + EoP
                    com1.sendData(pacote)
                    print("Confirmação final enviada.")
                    break
                    
            time.sleep(0.1)

        # Verifica se recebeu pelo menos alguns pacotes antes de salvar
        if len(image_buffer) > 0:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(imageW), exist_ok=True)
            
            # Salva a imagem recebida
            with open(imageW, 'wb') as f:
                f.write(image_buffer)

            print(f"\nImagem salva em {imageW}")
            print(f"Tamanho da imagem: {len(image_buffer)} bytes")
            print("\n")
        else:
            print("Nenhum dado ou dados insuficientes foram recebidos para salvar a imagem.")
            
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

if __name__ == "__main__":
    main()
