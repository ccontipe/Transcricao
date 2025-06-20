# CesarVox: Transcritor de Áudio e Gerador de Soluções Cloud (Modular)

Este projeto é uma aplicação desktop modular (Tkinter) desenvolvida em Python que combina a **transcrição de áudio** com a **geração inteligente de análises de negócio e propostas de solução técnica para ambientes Cloud (Azure, AWS, GCP)**, utilizando a API do Google Gemini. Além disso, gera diagramas de arquitetura (PlantUML C4) e scripts de Infraestrutura como Código (Terraform).

## Funcionalidades Principais

* **Transcrição de Áudio:** Converte arquivos de áudio (MP3, WAV, M4A, FLAC) em texto usando o modelo `Faster Whisper`. Suporte a uso de GPU (CUDA) para aceleração.

* **Análise de Problemas de Negócio:** Utiliza IA (Google Gemini) para analisar a transcrição gerada, identificando o problema central, premissas (explícitas e ocultas), restrições, stakeholders e próximos passos da discussão.

* **Geração de Propostas de Solução Técnica Cloud:** Gera propostas detalhadas de solução para a plataforma Cloud selecionada (Microsoft Azure, Amazon Web Services - AWS ou Google Cloud Platform - GCP). As propostas são alinhadas com padrões de arquitetura (microsserviços), frameworks Well-Architected da nuvem específica e considerações de segurança (PCI SSC).

* **Geração de Diagramas de Arquitetura (PlantUML C4):** Cria diagramas de contexto (C1), contêineres (C2), componentes (C3) e de sequência no formato PlantUML, baseados na solução técnica proposta.

* **Geração de Scripts Terraform (Infraestrutura como Código - IaC):** Gera exemplos de scripts Terraform (`.tf`) para provisionar os recursos da solução na nuvem escolhida, seguindo as melhores práticas e referenciando variáveis e segredos de forma segura.

* **Interface Gráfica Intuitiva:** Uma interface de usuário simples baseada em Tkinter para facilitar a interação.

## Estrutura do Projeto

O projeto é altamente modularizado para clareza, manutenção e escalabilidade, com a seguinte organização:

### Módulos Principais (na raiz do projeto)

* `main_app.py`: O ponto de entrada da aplicação. Orquestra a interface gráfica (GUI) e o fluxo principal de trabalho, chamando outros módulos em sequência.
* `audio_transcriber.py`: Responsável por toda a lógica de transcrição de áudio, incluindo instalação de dependências e execução do modelo Whisper.
* `problem_analyzer.py`: Encapsula a lógica para formular o prompt de análise de negócio e interagir com a API do Google Gemini para essa finalidade.
* `solution_generator.py`: Atua como o orquestrador principal para a geração da solução técnica. Ele delega a lógica específica de cada nuvem para os módulos em `solution_modules/` e o salvamento de arquivos para os módulos em `output_writers/`.

### solution_modules/ (Pacote de Módulos de Solução por Plataforma)

Este diretório contém os módulos especializados que geram as propostas de solução, diagramas e scripts Terraform, com base na plataforma de nuvem selecionada.

* `__init__.py`: Marca o diretório como um pacote Python.
* `solution_generator_azu.py`: Lógica e prompts específicos para gerar soluções para **Microsoft Azure**.
* `solution_generator_aws.py`: Lógica e prompts específicos para gerar soluções para **Amazon Web Services (AWS)**.
* `solution_generator_gcp.py`: Lógica e prompts específicos para gerar soluções para **Google Cloud Platform (GCP)**.

### output_writers/ (Pacote de Módulos de Escrita de Saída)

Este diretório contém os módulos que tratam exclusivamente do salvamento dos artefatos gerados (diagramas e scripts de infraestrutura) no sistema de arquivos.

* `__init__.py`: Marca o diretório como um pacote Python.
* `plantuml_writer.py`: Gerencia o salvamento de arquivos de diagrama PlantUML (`.puml`).
* `terraform_writer.py`: Gerencia o salvamento de arquivos de Infraestrutura como Código Terraform (`.tf`), organizando-os em subpastas específicas da plataforma.

### Arquivo de Log

* `voxLOG.txt`: O arquivo onde os logs de execução da aplicação são registrados, útil para depuração e acompanhamento.

## Como Usar

### Pré-requisitos

* Python 3.9+ instalado.
* Conexão com a internet para instalação de pacotes e chamadas à API da Google Gemini.
* **Chave de API do Google Gemini:** Obtenha uma chave de API em [Google AI Studio](https://aistudio.google.com/). Você precisará inseri-la no script `main_app.py`.
* Opcional: Uma GPU compatível com CUDA para transcrição mais rápida (requer instalação específica do `torch` com suporte a CUDA).

### Instalação

1.  **Clone o Repositório:**

    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Instale as Dependências:**

    Os módulos `audio_transcriber.py` e outros tentarão instalar automaticamente `faster-whisper`, `torch` e `google-generativeai` na primeira execução. No entanto, é **altamente recomendável** instalá-los manualmente em um ambiente virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    # ou .\venv\Scripts\activate # Windows
    
    # Instalação básica (CPU):
    pip install faster-whisper torch google-generativeai
    
    # Se você tem GPU NVIDIA e CUDA, instale a versão com CUDA (verifique a versão CUDA no site do PyTorch):
    # pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118) # Exemplo para CUDA 11.8
    # pip install faster-whisper google-generativeai
    ```

### Configuração da API Key

Abra o arquivo `main_app.py` e localize a linha:

```python
API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # Lembre-se de substituir pela sua chave real ou usar variável de ambiente mais segura
