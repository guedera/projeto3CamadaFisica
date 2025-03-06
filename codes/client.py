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
        # clear_terminal()

        #Handshake
        comprimento = False
        handshake_max_retries = 3  # Máximo de 3 tentativas para o handshake
        handshake_timeout = 5  # Timeout de 5 segundos para cada tentativa
        
        for attempt in range(handshake_max_retries):
            com1.rx.clearBuffer()

            print("-------------------------")
            print(f"Tentando Handshake (Tentativa {attempt+1} de {handshake_max_retries})")
            print("-------------------------")

            load_hs = b'0'
            txBuffer = datagrama(load_hs,1,1,0,0,numero_server,0) #handshake client = 1, handshake server = 2, dados = 3, eop certo = 4, timeou = 5, erro = 6

            com1.sendData(txBuffer)
            print("Pacote de handshake enviado!")

            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))
            time.sleep(0.5)

            print("Esperando resposta...")
            
            # Registra o tempo de início para controle do timeout
            start_handshake_time = time.time()
            
            # Loop que aguarda resposta com timeout, similar ao do servidor
            while not comprimento and (time.time() - start_handshake_time) < handshake_timeout:
                if com1.rx.getBufferLen() >= 15:
                    head, _ = com1.getData(12)  # Obtém os 12 bytes do header
                    eop, _ = com1.getData(3)    # Obtém os 3 bytes do EoP
                    
                    if check_h0(head, 2) and eop == b'\xAA\xBB\xCC': #check se o pacote é de handshake (2 pelo server)
                        print("Handshake confirmado!")
                        comprimento = True  # sai do loop do handshake
                        com1.rx.clearBuffer()
                        # clear_terminal()
                    else:
                        print("Handshake falhou! Resposta inválida.")
                        com1.rx.clearBuffer()
                
                # Evita consumo excessivo de CPU
                time.sleep(0.1)
            
            # Se o handshake foi bem-sucedido, sai do loop de tentativas
            if comprimento:
                break
                
            print(f"Timeout! Não recebeu resposta do servidor após {handshake_timeout} segundos.")

        # Verifica se o handshake foi bem-sucedido após as tentativas
        if not comprimento:
            print("Falha no handshake após 3 tentativas. Encerrando o programa.")
            com1.disable()
            return  # Encerra a função main
            
        # O resto do código permanece o mesmo para o envio da imagem
        imageR = "/home/guedera/Documents/Aulas/Camadas/projeto3CamadaFisica/codes/img/image.png"
        bytes_imagem = open(imageR, 'rb').read() #imagem em sequencia de bytes
        bytes_partes = separa(bytes_imagem) #separa a imagem em partes de no max 70 bytes e coloca numa lista

        i = 1
        print(len(bytes_partes))
        while i <= len(bytes_partes):
            time.sleep(0.5)
            data = datagrama(bytes_partes[i-1],i,3,0,0,numero_server,len(bytes_partes))
            txBuffer = data
            com1.sendData(txBuffer)            
            txSize = com1.tx.getStatus()
            print('enviou = {} bytes!' .format(txSize))

            print("Pacote {} enviado!".format(i))
            
            # Implementação do timeout
            timeout = 5  # 5 segundos de timeout
            max_retries = 3  # Máximo de 3 tentativas
            retries = 0
            response_received = False
            
            while retries < max_retries and not response_received:
                # Registra o tempo de início
                start_time = time.time()
                
                # Aguarde até que haja pelo menos 15 bytes para ler ou timeout
                while com1.rx.getBufferLen() < 15 and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                # Se conseguiu dados suficientes
                if com1.rx.getBufferLen() >= 15:
                    rxBuffer, _ = com1.getData(15)
                    
                    if certo(rxBuffer, i):
                        print("Pacote {} confirmado!".format(i))
                        print("Iniciando envio do próximo pacote...")
                        i += 1
                        com1.rx.clearBuffer()
                        time.sleep(0.5)
                        response_received = True
                    else:
                        print("Resposta incorreta recebida. Enviando o pacote {} novamente!".format(i))
                        time.sleep(.5)
                        retries += 1
                        com1.rx.clearBuffer()
                        com1.sendData(txBuffer)
                        print("Retentativa {} de {}".format(retries, max_retries))
                        time.sleep(0.5)
                else:
                    # Timeout ocorreu
                    print("Timeout! Nenhuma resposta recebida. Enviando o pacote {} novamente!".format(i))
                    retries += 1
                    com1.rx.clearBuffer()
                    
                    if retries < max_retries:
                        com1.sendData(txBuffer)
                        print("Retentativa {} de {}".format(retries, max_retries))
                    else:
                        # Enviar pacote de timeout (tipo 5)
                        timeout_packet = datagrama(b'', i, 5, 0, 0, numero_server, len(bytes_partes))
                        com1.sendData(timeout_packet)
                        print("Máximo de retentativas atingido. Enviando pacote de notificação de timeout.")
                        time.sleep(1)
                    
                    time.sleep(0.5)
            
            # Se todas as tentativas falharam
            if not response_received:
                print("Falha no envio do pacote {}. Encerrando transmissão.".format(i))
                break
        
        print("Confirmando que tudo foi enviado recebido no server corretamente!")
        
        # Implementa timeout para a confirmação final
        final_timeout = 5  # 5 segundos para timeout final
        start_final_time = time.time()
        final_confirmation = False
        
        # Aguarde até que haja pelo menos 15 bytes para ler OU até timeout
        while com1.rx.getBufferLen() < 15 and (time.time() - start_final_time) < final_timeout:
            time.sleep(0.1)
        
        # Verifica se recebeu dados ou se houve timeout
        if com1.rx.getBufferLen() >= 15:
            rxBuffer, _ = com1.getData(15)
            
            if certo(rxBuffer, len(bytes_partes)):
                print("Confirmação final recebida! Pacote {} confirmado!".format(len(bytes_partes)))
                print("Imagem enviada com sucesso!")
            else:
                print("Erro na confirmação final do pacote!")
        else:
            print("Timeout na confirmação final! Sem resposta do servidor.")
            
        time.sleep(0.5)
        # clear_terminal()
        
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