from enlace import *
import time
import numpy as np
from autolimpa import clear_terminal
from recebe_datagrama import *


serialName = "/dev/ttyACM0"

def main():
    try:
        timeout = 5
        handshake = False
        machine_state = {
            'one',
            'two'
        }
        start_time = time.time()
        numero_servidor = 8
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

        #se isso é verdade, então necwssariamente é tipo 1

        while not handshake:
            if com1.rx.getBufferLen() >=15:
                    head, nRx = com1.getData(12) #12 pq ele tem q ler o head primeiro
                    EoP, len_EoP = com1.getData(3)
                    h0,h1,h2,h3,h4,h5,h6,h7,_,_,_,_ = interpreta_head(head)
                    if verifica_dadosEoP(EoP):
                        if h5 == numero_servidor:
                            #servidor oscioso.
                            handshake = True
                            head = altera_byte(head,2)
                            pacote = head + EoP
                            com1.sendData(pacote)
                            contador = 1
                            numpckt = h4
                            total_pkct = h2
                            tamanho_pl = h3

        while numpckt < contador:
            #significa que não está no ultimo pacote.
            timer_reenvio = time.time()
            timer_desistir = time.time()

                #como verificar o payload ?
            while com1.rx.getBufferLen() != tamanho_pl+15:
                time.sleep(1.0)

        
                if timer_reenvio - time.time() > 0  :
                    #envia o tipo 5
                    break 

                else:
                    if timer_desistir - time.time() > 0:
                        #tipo 4, mas onde fiz a verificação que está sendo falada ? 
                        timer_reenvio = time.time()
                        continue




                else:


        

        else : 
            print("Acabou!!")


        


            

        






    
        h0,h1,_,h3,h4,h5,h6,h7,_,_,_,_ = interpreta_head(head)
        #h0: tipo msg / h3: numero total de pckt arquivo/ h4: numero do pacote/ h5: handshake ou dado/ 
        # h6: pckt solicitado recomeço/ h7:numero pcktultimo sucesso

        
        if verifica_tipo(h0,h1) == 'Tipo1':
           

           
            #como a mesnagem do itpo 1 não tem payload, ent tem que ter 3 de len
            EoP = com1.getData(3)


            #mandar sinal de ocioso:
            com1.sendData(altera_byte(head,2))
            n=1
            time.sleep(.5)
        
        elif verifica_tipo(h0,h1) == 'Tipo3':
            
            n+=1
            PayLoad = com1.getData(h3)
            verifica = verifica_erro(h0,h5,h6,h7,PayLoad,n)
            if  verifica =='Verificado':
                total_pkct = h3
                numero_pckt_recebido = h4 #Numero do pacote recebido de acordo com o client.
                com1.sendData(altera_byte(head,4,h4))
            else:
                l_erros = verifica.split("\n")
                for erro in l_erros:
                    com1.sendData(erro.encode('utf-8'))

        EoP = com1.rx.buffer
        if verifica_dadosEoP(len(EoP))!= 'True':
            com1.sendData(altera_byte(head,6,n))

            

        elif (time.time() - start_time) > timeout:
            #time out 
            com1.sendData(altera_byte(head,5))
            print("\n")
            print("\n")
            print("Comunicação encerrada devido ao timeout.")
            print("-------------------------")
            com1.disable()       
            
        
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
