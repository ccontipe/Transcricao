# 🧠 CesarVox - Transcritor Inteligente com Análise de Negócios (faster-whisper + Gemini)

Este projeto é uma aplicação de interface gráfica (GUI) em Python chamada **CesarVox**, projetada para transcrição de áudios e análise automatizada com foco em conteúdo de reuniões, palestras e discussões técnicas.

## 🚀 Funcionalidades

- 🎙️ Transcrição de áudios usando o modelo [faster-whisper](https://github.com/guillaumekln/faster-whisper), com suporte a CUDA (GPU) ou CPU.
- 🧠 Análise automatizada de conteúdo com o modelo **Gemini 1.5** da Google (via `google-generativeai`), voltada para:
  - Extração de premissas (explícitas e implícitas)
  - Identificação de problemas, restrições e próximos passos
  - Mapeamento de stakeholders e seus interesses
- 📋 Interface gráfica com `Tkinter`, oferecendo:
  - Seleção de modelo Whisper
  - Escolha de arquivos de entrada e saída
  - Indicador de progresso da transcrição
  - Cancelamento em tempo real

## 🧩 Dependências

Instalação automática ao rodar o script (se não instaladas):

- `faster-whisper`
- `torch`
- `google-generativeai`

## 🔐 API Key Gemini

Para usar a análise com o modelo Gemini, é necessário definir a variável de ambiente:

```bash
set GEMINI_API_KEY=your-api-key-aqui
```

## 🖥️ Requisitos

- Python 3.8+
- Conexão com a internet para instalar pacotes e acessar a API do Gemini
- Opcional: GPU com suporte CUDA para aceleração da transcrição

## 📦 Execução

Execute o script diretamente:

```bash
python transcrever-5.py
```

A interface será carregada com campos para:
- Selecionar o áudio de entrada (`.mp3`, `.wav`, `.flac`, etc.)
- Escolher o modelo (ex: `small`, `medium`)
- Decidir se deseja gerar a análise automatizada com Gemini
- Selecionar uso de GPU (se disponível)

## 🗃️ Saídas

- Arquivo `.txt` contendo a transcrição bruta
- Opcional: Arquivo `.txt` contendo a **análise estruturada** gerada pelo Gemini

## 📁 Log

Todas as atividades e erros são registrados em:

```text
voxLOG.txt
```

Inclui: progresso, erros de transcrição, falhas de rede/API, e status da GPU.

## 📌 Observações

- O script respeita a ausência de GPU e executa em CPU automaticamente.
- Se a API Key do Gemini não estiver configurada, a análise será desativada automaticamente.
- Não há uso de Logic Apps ou integrações externas além da API do Google.

---

© 2025 Cesar Contipelli - Todos os direitos reservados.
