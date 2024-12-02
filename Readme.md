Aplicação de Leitura de Textos a partir de Fotos

Descrição do Projeto:
Este projeto é uma aplicação para auxiliar pessoas com deficiência visual a ler textos em imagens focado na acessibilidade de conteúdos textuais de livros físicos. Utilizando tecnologias de reconhecimento óptico de caracteres (OCR) e síntese de fala, a aplicação permite que o usuário capture a página de um livro, e o sistema realiza a extração e leitura em áudio do conteúdo textual. Esta solução proporciona maior autonomia para pessoas com deficiência visual, facilitando o acesso à informação escrita.

Funcionalidades:
 - Captura de imagens para análise;
 - Extração de texto utilizando uma biblioteca de OCR;
 - Síntese de áudio utilizando a bíblioteca gTTS;

Tecnologias Utilizadas:
 - Frontend: React e React Native;
 - Backend: Flask; 
 - OCR (Reconhecimento Óptico de Caracteres): Tesseract.js, EasyOCR;
 - Pré processamento de imagem: OpenCV;
 - Síntese de áudio: gTTS
 - Banco de Dados: PostgreSQL;
 - Outras Ferramentas: Docker.

Pré-requisitos
Antes de começar, certifique-se de ter os seguintes itens instalados:
 - Python 3.12; 
 - Docker; 
 - Biblioteca OCR: <https://sourceforge.net/projects/tesseract-ocr.mirror/>

 -> Além disso, também é necessário estar conectado à internet, e ter o cabo de conexão do seu celular em mãos, assim como o celular. 

Instalação:

    Para Windows e Linux com Docker:
    1 - Clone o repositório:
        git clone <https://github.com/Nathan-Brito/Voz_de_Papel_API.git>
        cd Voz_de_Papel_API
    
    2 - Certifique-se de ter o Docker instalado:
        Windows: Baixe e instale o Docker Desktop: <https://www.docker.com/>
        Linux: Siga as instruções de instalação no site oficial do Docker: <https://docs.docker.com/desktop/setup/install/linux/>

    3 - Inicie os containers:
        Execute o seguinte comando para criar e inicializar os containers definidos no docker-compose.yml:
        docker-compose up --build

    4 - Verifique o estado dos containers:
        Certifique-se de que o container do PostgreSQL e qualquer outro serviço relacionado estão em execução:
        docker ps

    5 - Acesse a API:
        A API estará disponível em:
       <https://ifms.pro.br:2007/image_to_audio>

    Para Windows sem Docker
    1 - Clone o repositório:
        git clone <https://github.com/Nathan-Brito/Voz_de_Papel_API.git>
        cd Voz_de_Papel_API

    2 - Crie um ambiente virtual Python:
        python -m venv venv
        venv\Scripts\activate

    3 - Instale as dependências:
        pip install -r requirements.txt

    4 - Configure o PostgreSQL:
        - Baixe e instale o PostgreSQL para Windows no site oficial: <https://www.postgresql.org/>
        - Configure o banco de dados com as credenciais especificadas no docker-compose.yml:
            - Usuário: vozpapeladm
            - Senha: VozPapelAdm
            - Banco: bdvozdepapel
            
    5 - Execute a aplicação:
        python app.py

    Para Linux sem Docker
    1 - Clone o repositório:
        git clone <https://github.com/Nathan-Brito/Voz_de_Papel_API.git>
        cd Voz_de_Papel_API

    2 - Crie um ambiente virtual Python:
        python3 -m venv venv
        source venv/bin/activate

    3 - Instale as dependências:
        pip install -r requirements.txt

    4 - Instale o PostgreSQL:
        - Execute os comandos:
            sudo apt update
            sudo apt install postgresql postgresql-contrib
            Configure o banco com os mesmos dados definidos no docker-compose.yml.

    5 - Execute a aplicação:
        python3 app.py

*Uso
    1 - Acesse a aplicação em <https://ifms.pro.br:2007/image_to_audio>;
    2 - Faça upload de uma imagem contendo texto.
    3 - Aguarde o processamento e veja o texto extraído na tela.