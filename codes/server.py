from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from recebe_datagrama import *
from separa import separa
from datagramas import datagrama
from certo import check_h0, certo

serialName = "/dev/ttyACM0"  # Importante: Ajuste para a porta correta no outro computador

def main():
    try:
        numero_servidor = 8
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        com1.rx.clearBuffer()

        print("Esperando byte de sacrifício")
        # Espera pelo byte de sacrifício (não bloqueante)
        timeout_count = 0
        max_timeout = 10  # 10 segundos de espera máxima
        
        while com1.rx.getBufferLen() < 1 and timeout_count < max_timeout:
            time.sleep(1)
            timeout_count += 1
            if timeout_count % 2 == 0:  # A cada 2 segundos
                print(f"Aguardando byte de sacrifício... ({timeout_count}s)")
                
        if timeout_count >= max_timeout:
            print("Timeout na espera pelo byte de sacrifício. Encerrando...")
            com1.disable()
            return
            
        sacrifice_byte, _ = com1.getData(com1.rx.getBufferLen())
        com1.rx.clearBuffer()
        print("Byte de sacrifício recebido")
        time.sleep(0.5)

        print("Abriu a comunicação!")
        print("Esperando handshake do cliente...")

        # Dados da imagem recebida
        file_bytes = bytearray()
        
        # Timeout para handshake
        timeout_handshake = 30  # 30 segundos para handshake
        start_time = time.time()
        handshake_received = False
        
        # Aguarda handshake do cliente
        while (time.time() - start_time < timeout_handshake) and not handshake_received:
            if com1.rx.getBufferLen() >= 15:  # Pelo menos cabeçalho + 1 byte payload + EOP (12+1+3)
                print("Dados recebidos! Verificando se é handshake...")
                
                # Lê o cabeçalho
                header, _ = com1.getData(12)
                h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11 = header
                
                # Verifica se é mensagem de handshake (tipo 1)
                if h0 == 1:
                    # Lê o payload e o EOP
                    payload_size = h3
                    payload, _ = com1.getData(payload_size)
                    eop, _ = com1.getData(3)
                    
                    # Verifica se é para este servidor e se o EOP está correto
                    if h5 == numero_servidor and eop == b'\xAA\xBB\xCC':
                        print("Handshake recebido do cliente!")
                        handshake_received = True
                        
                        # Responde com handshake (tipo 2)
                        resposta = datagrama(b'0', 0, 2, 0, 0, numero_servidor)
                        com1.sendData(resposta)
                        print("Handshake (tipo 2) enviado ao cliente")
                        
                        # Guarda informações do total de pacotes
                        total_packets = h1
                        print(f"Total de pacotes esperados: {total_packets}")
                        
                        expected_packet = 1  # Começa esperando o pacote 1
                        last_received = 0
                    else:
                        print(f"Handshake com servidor incorreto ou EOP inválido")
                        com1.rx.clearBuffer()
                else:
                    print(f"Recebido pacote tipo {h0}, esperava tipo 1 (handshake)")
                    com1.rx.clearBuffer()
            else:
                if (time.time() - start_time) % 5 < 0.1:  # Exibe mensagem a cada ~5 segundos
                    print("Aguardando handshake do cliente...")
                time.sleep(0.1)
        
        if not handshake_received:
            print("Timeout na espera pelo handshake. Encerrando...")
            com1.disable()
            return
        
        # Recepção de pacotes
        print("Iniciando recepção de pacotes")
        
        while last_received < total_packets:
            print(f"Esperando pacote {expected_packet}")
            
            # Espera até ter dados disponíveis
            while com1.rx.getBufferLen() < 12:  # Pelo menos o header
                time.sleep(0.1)
                
            # Lê o cabeçalho
            header, _ = com1.getData(12)
            h0, h1, h2, h3, h4, h5, h6, h7, _, _, _, _ = interpreta_head(header)
            
            # Verifica se é pacote de dados (tipo 3)
            if h0 == 3:
                payload_size = h3
                packet_number = h4
                
                # Espera pelo payload e EOP
                while com1.rx.getBufferLen() < payload_size + 3:
                    time.sleep(0.1)
                    
                # Lê o payload e o EOP
                payload, _ = com1.getData(payload_size)
                eop, _ = com1.getData(3)
                
                # Verifica integridade
                erro = False
                mensagem_erro = ""
                
                # Verifica se é o pacote esperado
                if packet_number != expected_packet:
                    erro = True
                    mensagem_erro += f"Erro na sequência. Esperado: {expected_packet}, Recebido: {packet_number}\n"
                
                # Verifica tamanho do payload
                if len(payload) != payload_size:
                    erro = True
                    mensagem_erro += f"Erro no tamanho do payload. Esperado: {payload_size}, Recebido: {len(payload)}\n"
                
                # Verifica EOP
                if not verifica_dadosEoP(eop):
                    erro = True
                    mensagem_erro += "EOP incorreto\n"
                
                # Processa conforme verificação
                if erro:
                    print(mensagem_erro)
                    # Envia mensagem de erro (tipo 6)
                    erro_resposta = datagrama(b'0', expected_packet, 6, expected_packet, last_received, numero_servidor)
                    com1.sendData(erro_resposta)
                    print(f"Enviando resposta de erro (tipo 6) solicitando pacote {expected_packet}")
                else:
                    # Adiciona ao arquivo
                    file_bytes.extend(payload)
                    
                    # Atualiza contadores
                    last_received = packet_number
                    expected_packet = packet_number + 1
                    
                    # Responde com sucesso (tipo 4)
                    sucesso_resposta = datagrama(b'0', packet_number, 4, 0, 1, numero_servidor)
                    com1.sendData(sucesso_resposta)
                    print(f"Pacote {packet_number} recebido com sucesso - Enviando resposta tipo 4")
                
            else:
                # Se não for tipo 3, limpa o buffer e continua
                print(f"Recebido pacote tipo {h0}, esperava tipo 3")
                com1.rx.clearBuffer()
        
        # Todos os pacotes recebidos
        print("Todos os pacotes recebidos com sucesso!")
        
        # Salvar o arquivo
        try:
            with open("img/imagecopy.png", "wb") as f:
                f.write(file_bytes)
            print("Imagem salva como img/imagecopy.png")
        except:
            # Cria pasta se não existir
            import os
            os.makedirs("img", exist_ok=True)
            with open("img/imagecopy.png", "wb") as f:
                f.write(file_bytes)
            print("Imagem salva como img/imagecopy.png")
        
        # Envia confirmação final
        final_resposta = datagrama(b'0', total_packets, 4, 0, 1, numero_servidor)
        com1.sendData(final_resposta)
        print("Enviada confirmação final")
        
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        print("Erro completo:", erro.__class__, erro)
        import traceback
        traceback.print_exc()
        com1.disable()

if __name__ == "__main__":
    main()