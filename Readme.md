# Voz de Papel

## Descrição do Projeto:
Este projeto é uma aplicação para auxiliar pessoas com deficiência visual a ler textos em imagens focado na acessibilidade de conteúdos textuais de livros físicos. Utilizando tecnologias de reconhecimento óptico de caracteres (OCR) e síntese de fala, a aplicação permite que o usuário capture a página de um livro, e o sistema realiza a extração e leitura em áudio do conteúdo textual. Esta solução proporciona maior autonomia para pessoas com deficiência visual, facilitando o acesso à informação escrita.

## Funcionalidades:
 - Extração de Texto: O aplicativo utiliza o Tesseract OCR para capturar e processar o texto presente na imagem enviada;
 - Correção e Refinamento: O texto extraído é refinado utilizando a API Gemini para melhorar a gramática e a coerência;
 - Conversão para Áudio: O texto é convertido em áudio utilizando a API Azure Speech Services, com suporte para a voz natural em português brasileiro;
 - Armazenamento de Logs: Informações sobre as requisições (IP de origem, imagem codificada, texto extraído, etc.) são armazenadas em um banco de dados PostgreSQL para fins de análise e rastreamento.

## Tecnologias Utilizadas:
 - Frontend: React Native;
 - Backend: Python Flask; 
 - OCR (Reconhecimento Óptico de Caracteres): Tesseract;
 - Pré processamento de imagem: OpenCV;
 - Síntese de áudio: API Azure Speech Services;
 - Banco de Dados: PostgreSQL;
 - Outras Ferramentas: Docker.

## Uso do Aplicativo (Somente para Android): 
    1 - Baixe 'Voz_De_Papel.apk', disponível em: <https://github.com/Nathan-Brito/Voz_de_Papel_API>;
    2 - Instale o aplicativo;
    3 - Abra o aplicativo e ouça atentamente as instruções de voz;
    4 - Capture a imagem seguindo as instruções;
    5 - Ouça o áudio da leitura:
        - Você pode pausar ou dar play no áudio enquanto estiver ouvindo;
        - Você pode voltar a câmera a qualquer momento clicando no botão 'Stop'.
    6 - Após seu áudio ser finalizado, clique no botão 'Stop' e volte a tela da câmera.  

## Uso da API:
    Esta API precisa ser usada por meio de requisição HTTP, com os seguintes endpoints:
    1 - <http://ifms.pro.br:2007/>: retorna uma mensagem 'Aplicação rodando!';
    2 - <http://ifms.pro.br:2007/image_to_audio>: requer uma imagem no corpo da requisição com a key 'image'. Essa requisição irá retornar um arquivo 'output_audio.mp3'; 
    3 - <http://ifms.pro.br:2007/logs>: requer um JSON com uma QUERY que seja um comando SELECT. Ele irá retornar um JSON com as respostas da requisição. 

## **PARA UTILIZAR O CÓDIGO**

## Pré-requisitos:
Antes de começar, certifique-se de ter os seguintes itens instalados:
 - Python 3.12; 
 - Docker; 
 - Biblioteca OCR: <https://sourceforge.net/projects/tesseract-ocr.mirror/>
    - Após instalação, digite no terminal:
        - plaintext
        - pip install tesseract

 -> Além disso, também é necessário estar conectado à internet, e ter o cabo de conexão do seu celular em mãos, assim como o celular. 

## Instalação:

**Para Windows e Linux com Docker:**

    1 - Clone o repositório:
        git clone <https://github.com/Nathan-Brito/Voz_de_Papel_API.git>
        cd Voz_de_Papel_API
    
    2 - Certifique-se de ter o Docker instalado:
        Windows: Baixe e instale o Docker Desktop: <https://www.docker.com/>
        Linux: Siga as instruções de instalação no site oficial do Docker: <https://docs.docker.com/desktop/setup/install/linux/>

    3 - Inicie os containers:
        Execute o seguinte comando para criar e inicializar os containers definidos no docker-compose.yml:
        docker-compose up --build
        - Certifique-se que o arquivo 'init.sql' esteja na mesma pasta que o 'docker-compose.yml'

    4 - Verifique o estado dos containers:
        Certifique-se de que o container do PostgreSQL e qualquer outro serviço relacionado estão em execução:
        docker ps

    5 - Crie um ambiente virtual Python:
        python -m venv venv
        venv\Scripts\activate

    6 - Instale as dependências:
        pip install -r requirements.txt

    7 - Criação das variáveis de ambiente: 
        - Crie um arquivo '.env' na raiz do projeto;
        - Configure as seguintes chaves: 
            AZURE_KEY=<sua chave da API Azure>
            AZURE_REGION=<sua região da API Azure>
            GEMINI_KEY=<sua chave da API Gemini>
            DBNAME=<seu nome do banco de dados>
            DBUSER=<seu usuário do banco de dados>
            DBKEY=<senha do seu banco de dados>
            DBHOST=<endereço IP do seu host>
            DBPORT=<a porta do seu banco de dados>

    8 - Execute a aplicação:
        python app.py

**Para Windows sem Docker:**

    1 - Clone o repositório:
        git clone <https://github.com/Nathan-Brito/Voz_de_Papel_API.git>
        cd Voz_de_Papel_API

    2 - Crie um ambiente virtual Python:
        python -m venv venv
        venv\Scripts\activate

    3 - Instale as dependências:
        pip install -r requirements.txt

    4 - Criação das variáveis de ambiente: 
        - Crie um arquivo '.env' na raiz do projeto;
        - Configure as seguintes chaves: 
            AZURE_KEY=<sua chave da API Azure>
            AZURE_REGION=<sua região da API Azure>
            GEMINI_KEY=<sua chave da API Gemini>
            DBNAME=<seu nome do banco de dados>
            DBUSER=<seu usuário do banco de dados>
            DBKEY=<senha do seu banco de dados>
            DBHOST=<endereço IP do seu host>
            DBPORT=<a porta do seu banco de dados>

    5 - Configure o PostgreSQL:
        - Baixe e instale o PostgreSQL para Windows no site oficial: <https://www.postgresql.org/>
        - Configure o banco de dados com as credenciais especificadas:
            - Usuário: <seu usuário>
            - Senha: <sua senha>
            - Banco: <nome do banco de dados>
            
    6 - Execute a aplicação:
        python app.py

**Para Linux sem Docker:**

    1 - Clone o repositório:
        git clone <https://github.com/Nathan-Brito/Voz_de_Papel_API.git>
        cd Voz_de_Papel_API

    2 - Crie um ambiente virtual Python:
        python3 -m venv venv
        source venv/bin/activate

    3 - Instale as dependências:
        pip install -r requirements.txt

    4 - Criação das variáveis de ambiente: 
        - Crie um arquivo '.env' na raiz do projeto;
        - Configure as seguintes chaves: 
            AZURE_KEY=<sua chave da API Azure>
            AZURE_REGION=<sua região da API Azure>
            GEMINI_KEY=<sua chave da API Gemini>
            DBNAME=<seu nome do banco de dados>
            DBUSER=<seu usuário do banco de dados>
            DBKEY=<senha do seu banco de dados>
            DBHOST=<endereço IP do seu host>
            DBPORT=<a porta do seu banco de dados>

    5 - Instale o PostgreSQL:
        - Execute os comandos:
            sudo apt update
            sudo apt install postgresql postgresql-contrib
            
        - Configure o banco de dados com as credenciais especificadas:
            - Usuário: <seu usuário>
            - Senha: <sua senha>
            - Banco: <nome do banco de dados>

    6 - Execute a aplicação:
        python3 app.py

## Estrutura do Projeto:
```plaintext 
.
├── Voz_De_Papel.apk   # Apk da aplicação
├── app.py/            # Código do backend
├── docker-compose.yml # Arquivo para orquestração com Docker
├── README.md          # Este arquivo
├── init.sql           # Inicialização do Banco de Dados
└── requirements.txt   # Bibliotecas para instalação do ambiente virtual
```

## Link para a Documentação Completa:  
<https://tinyurl.com/Documentacao-Voz-De-Papel>
