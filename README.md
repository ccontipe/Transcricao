### **Conteúdo para o Arquivo `README.md`**

```markdown
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

O projeto é altamente modularizado para clareza, manutenção e escalabilidade:

```
/seu_repositorio/
│
├── main_app.py                   # Módulo Principal: Orquestra a GUI e o fluxo.
├── audio_transcriber.py          # Módulo 2: Lógica de transcrição de áudio.
├── problem_analyzer.py           # Módulo 3: Lógica de análise de problemas de negócio com GEM.
├── solution_generator.py         # Módulo 4: Orquestrador. Delega a geração da solução para a nuvem específica e coordena o parsing/salvamento.
│
├── solution_modules/             # Pacote: Contém a lógica e prompts específicos para cada plataforma Cloud.
│   ├── __init__.py
│   ├── solution_generator_azu.py # Gerador de solução para Microsoft Azure.
│   ├── solution_generator_aws.py # Gerador de solução para Amazon AWS.
│   └── solution_generator_gcp.py # Gerador de solução para Google Cloud Platform.
│
├── output_writers/               # Pacote: Contém módulos para salvar os artefatos gerados.
│   ├── __init__.py
│   ├── plantuml_writer.py        # Salva arquivos PlantUML.
│   └── terraform_writer.py       # Salva arquivos Terraform.
│
└── voxLOG.txt                    # Arquivo de log da aplicação.
```

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
API_KEY = "AIzaSyBrFE5AJuUzdRc9ysfasimGTfeowywvkFs" # Lembre-se de substituir pela sua chave real ou usar variável de ambiente mais segura
```
Substitua `"AIzaSyBrFE5AJuUzdRc9ysfasimGTfeowywvkFs"` pela sua chave de API real do Google Gemini.

### Execução

1.  Ative seu ambiente virtual (se ainda não estiver ativo).
2.  Execute o script principal:
    ```bash
    python main_app.py
    ```

### Fluxo de Uso da Aplicação

1.  **Selecione um Arquivo de Áudio:** Clique em "Procurar" para escolher seu arquivo de áudio (`.mp3`, `.wav`, etc.).
2.  **Defina o Arquivo de Saída da Transcrição:** O sistema sugerirá um nome, mas você pode alterá-lo clicando em "Salvar".
3.  **Escolha o Modelo Whisper:** Selecione o tamanho do modelo (`tiny`, `base`, `small`, `medium`, `large`). Modelos maiores oferecem melhor precisão, mas são mais lentos e exigem mais recursos.
4.  **Marque Opções de Geração:**
    * `Usar GPU (se disponível)`: Acelera a transcrição se você tiver uma GPU compatível com CUDA.
    * `Gerar Análise`: Ativa a análise de negócio da transcrição pela IA.
    * `Gerar Solução`: Ativa a geração da proposta de solução técnica, incluindo diagramas e Terraform.
5.  **Se 'Gerar Solução' estiver marcado, selecione a Plataforma Cloud:** Escolha entre Azure, AWS ou GCP.
6.  **Clique em "Transcrever":** O processo iniciará em segundo plano.
7.  **Monitore o Progresso:** A barra e o label de progresso na GUI serão atualizados.
8.  **Resultados:** Após a conclusão, mensagens de sucesso aparecerão, e os arquivos serão gerados:
    * `Transcricao-NomeAudio.txt`: O texto bruto da transcrição.
    * `GEM - Analise NomeAudio.txt`: A análise de negócio (se selecionado).
    * `GEM - Solucao Tecnica (Plataforma) NomeAudio.txt`: O texto principal da proposta de solução.
    * `PlantUML - *.puml`: Arquivos de diagrama PlantUML (C1, C2, C3, Sequência) no diretório de saída.
    * `Terraform_Plataforma_NomeAudio/`: Uma pasta contendo os arquivos Terraform (`versions.tf`, `providers.tf`, `variables.tf`, `main.tf`, `outputs.tf`) para a infraestrutura da solução.

## Contribuição

Sinta-se à vontade para contribuir com este projeto!

---
```