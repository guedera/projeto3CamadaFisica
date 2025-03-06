from separa import separa

def datagrama(bytes_entrada,n_pacote:int,tipo:int,erro:int,sucesso:int,id:int, pacotes:int) -> list:
    h0 = tipo.to_bytes(1, 'big') #handhsake client = 1, handshake server = 2, dados = 3, eop certo = 4, timeou = 5, erro = 6
    h1 = tipo.to_bytes(1, 'big')
    h2 = tipo.to_bytes(1, 'big')
    h3 = pacotes.to_bytes(1, 'big')
    h4 = n_pacote.to_bytes(1, 'big')
    h5 = b'\x00'
    if tipo == 1: #handshake
        h5 = id.to_bytes(1, 'big') #Convert integer id to bytes
    elif tipo == 3:
        h5 = len(bytes_entrada).to_bytes(1, 'big') #mudar

    h6 = erro.to_bytes(1, 'big') #mudar
    h7 = sucesso.to_bytes(1, 'big') #mudar
    h8 = b'0' #projeto 5 
    h9 = b'0' #projeto 5
    h10 = b'0' #livre
    h11 = b'0' #livre    
    EoP = b'\xAA\xBB\xCC'
    return (h0+h1+h2+h3+h4+h5+h6+h7+h8+h9+h10+h11+bytes_entrada+EoP)

#Exemplo de uso
if False:
    data = b'\x10]\xe9q\x12U\x1c\x12&9\xc0\xf1\x947\xb4\xb6\xc0\xcc\xd1\xc7\x90\x03\xc1\xd4v(\xa7o\x9e\\o\x08e;\x13\xdd\xe4+s\xe0\x99\x01\xaf\x8e\',\x06\x85\xedLi\xd2V\x91/\x8f\x1b9\x9b@\xa5\x11\xbb@\xa3\x96A@6\x118o\xc0\x7fo\x1b\xba\x1f\xa8\xe7\xbb\xc7\xc2\xf9\x8e\xec\xf1\t\x0e\x9d\xf9\\\xcdA\x17I\xb2.\x96^\x9f\xfc\x1eN\xa9\xb8\xbb\x90Z\xd3\x07\xdf\x8d\xab\n77\x9fQ\x84\x9eC\xa9\xceL\xf9\xf6\x9eM\xc9\x131\xfa:J\xb2\x88\x8bw\xf6~\x0eR\x91\xc3\xa0\xeb\xa9n\xb2\xf4\xb8*:\x9b\xe3\xa4\x0e\xf6@\xa2\xe4\xea\x97\xdc\xb0d\x00\x87\x03\xce\xa6\xee\xf1\xa0\x01\x95\xb4\xedUi\x13\xb3Fzr\x0b\xce\xf6l\xea\xd8/\xd6\xf4\xde\xae\xe6aW\x04!\xaa\xd4Q\xe9\x18S\x10\x18p\xd2\xbf:\xdb\noGX\xff\x81\xce/\x03Kk0y\xe6\xe2\xd6qa\x11\x1d\xa0Y\xe2\x98\x9c\xf6\\\x97'

    partes = separa(data)
    print(len(partes[0]))

    final = datagrama(partes[0],0,1,0,0)
    print(final)
    print(type(final))
    print(len(final))