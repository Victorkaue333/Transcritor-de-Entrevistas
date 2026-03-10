# Whisper Interview Transcriber

Automação em Python para transcrever entrevistas a partir de arquivos de áudio ou vídeo, gerando uma transcrição completa com timestamps, segmentação por trechos e exportação em múltiplos formatos.

## Objetivo

Este projeto foi criado para facilitar a transcrição de entrevistas acadêmicas, reuniões e gravações em geral.

A aplicação recebe um arquivo de áudio ou vídeo, processa o conteúdo com o modelo Whisper e gera:

- transcrição completa em texto
- segmentação por tempo
- arquivo JSON estruturado
- arquivo SRT com legendas

## Funcionalidades

- leitura de arquivos `.mp4`, `.mp3`, `.wav`, `.m4a`
- transcrição automática em português
- separação por segmentos com timestamp
- exportação em:
  - `.txt`
  - `.json`
  - `.srt`
- organização simples para uso em pesquisa acadêmica

## Estrutura do projeto

```bash
whisper-interview-transcriber/
│
├── docs/
├── input/
├── logs/
├── output/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── cleaner.py
│   ├── cli.py
│   ├── config.py
│   ├── exporter.py
│   ├── formatter.py
│   ├── logger.py
│   ├── metadata.py
│   ├── transcriber.py
│   ├── utils.py
│   └── services/
│       └── transcript_service.py
│
├── main.py
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10+
- FFmpeg instalado no sistema
- pip atualizado

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/whisper-interview-transcriber.git
cd whisper-interview-transcriber
```

### 2. Crie e ative um ambiente virtual

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## Instalação do FFmpeg

O Whisper precisa do FFmpeg para processar arquivos de áudio e vídeo.

### Windows
Baixe o FFmpeg e adicione ao PATH do sistema.

### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

## Como usar

1. Coloque o arquivo da entrevista dentro da pasta `input/`
2. Renomeie para `entrevista.mp4` ou ajuste o nome no `main.py`
3. Execute:

```bash
python main.py
```

## Saídas geradas

Os arquivos serão salvos na pasta `output/`:

- `transcript.txt` → transcrição formatada com timestamps
- `transcript.json` → transcrição estruturada em JSON
- `transcript.srt` → legendas em formato SRT

## Exemplo de saída em TXT

```text
[00:00:00 --> 00:00:08]
Olá, bom dia. Hoje estamos aqui com o convidado...

[00:00:08 --> 00:00:16]
A etnia do nosso convidado é a Pancará...
```

## Limitações atuais

- a separação automática por falante depende de diarização, que não está incluída nesta primeira versão
- o Whisper transcreve muito bem, mas não identifica nomes dos participantes sozinho
- para identificar "Victor", "Thalysson" e "Francisco", é possível integrar diarização em uma próxima versão


## Logs da aplicação

O projeto utiliza a biblioteca nativa `logging` do Python para registrar a execução da aplicação.

Os logs são exibidos no terminal e também salvos em:

```bash
logs/app.log
```

Eles registram:

- início da execução
- arquivo processado
- modelo do Whisper usado
- erros
- arquivos exportados


## Melhorias futuras

- diarização de falantes
- interface web com upload de arquivos
- exportação em DOCX
- limpeza automática de repetições e ruídos
- sumarização automática por temas