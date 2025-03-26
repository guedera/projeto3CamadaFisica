# Projeto 3 - Camada Física da Computação

Este projeto implementa a comunicação entre um cliente e um servidor utilizando a camada física da computação. Ele simula a transmissão de dados (como imagens) em pacotes, com controle de erros, confirmações e timeouts.

## Estrutura do Projeto

- **Cliente (`client.py`)**: Envia os dados para o servidor em pacotes. Implementa o handshake inicial, separação dos dados em partes menores e retransmissão em caso de falhas.
- **Servidor (`server.py`)**: Recebe os pacotes enviados pelo cliente, verifica erros e confirma a recepção. Reconstrói os dados recebidos e os salva em um arquivo.
- **Camada de Enlace (`enlace.py`)**: Gerencia a comunicação entre cliente e servidor, utilizando as classes `TX` e `RX` para envio e recepção de dados.
- **Utilitários**:
  - `datagramas.py`: Cria os pacotes de dados com cabeçalhos e delimitadores.
  - `separa.py`: Divide os dados em partes menores para envio.
  - `recebe_datagrama.py`: Interpreta os cabeçalhos dos pacotes recebidos.
  - `certo.py`: Verifica a validade dos pacotes recebidos.
  - `autolimpa.py`: Limpa o terminal para melhor visualização.

## Funcionamento

1. **Handshake**: O cliente inicia a comunicação enviando um pacote de handshake. O servidor responde confirmando a conexão.
2. **Envio de Dados**: O cliente divide os dados em pacotes e os envia sequencialmente. Cada pacote contém um cabeçalho com informações como número do pacote e tamanho do payload.
3. **Confirmação**: O servidor confirma a recepção de cada pacote. Em caso de erro, solicita o reenvio.
4. **Reconstrução**: O servidor reconstrói os dados recebidos e os salva em um arquivo.
5. **Finalização**: Após o envio de todos os pacotes, o cliente e o servidor encerram a comunicação.

## Requisitos

- Python 3
- Biblioteca `pyserial` para comunicação serial

## Como Executar

1. Conecte os dispositivos (cliente e servidor) via porta serial.
2. No servidor, execute:
   ```bash
   python3 server.py
   ```
3. No cliente, execute:
   ```bash
   python3 client.py
   ```
4. Acompanhe os logs no terminal para verificar o progresso da comunicação.

## Estrutura de Arquivos

- `codes/`: Contém todos os scripts do projeto.
- `img/`: Diretório para armazenar as imagens enviadas e recebidas.
- `.gitignore`: Ignora arquivos desnecessários como `__pycache__`.

## Observação

Certifique-se de configurar as portas seriais corretamente nos arquivos `client.py` e `server.py` antes de executar o projeto.
