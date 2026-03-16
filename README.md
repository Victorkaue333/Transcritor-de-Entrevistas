# 💡 Transcritor de Entrevistas com Whisper e PyAnnote

> Sistema web de transcrição automática de áudio e vídeo com navegação por timestamps, identificação de speakers e exportação em múltiplos formatos.

Uma aplicação full-stack que utiliza o modelo Whisper da OpenAI para transcrever entrevistas, reuniões e gravações, oferecendo uma interface interativa para navegação sincronizada entre vídeo e texto transcrito.

---

## 📺 Demonstração

<!-- Adicione aqui screenshots ou GIF da aplicação -->

**Recursos visuais:**

- Interface com player de vídeo sincronizado
- Lista de segmentos clicáveis com timestamps
- Busca em tempo real na transcrição
- Botões de download (TXT, JSON, SRT)
- Checkbox para identificação de speakers

---

## 🎯 Problema que o projeto resolve

O problema foi vivenciado por mim mesmo durante a tentativa de transcrição manual de entrevistas para um projeto acadêmico. O processo era extremamente demorado, especialmente para gravações longas, e havia dificuldades para localizar trechos específicos, identificar quem estava falando de acordo com a voz e também para exportar o conteúdo em formatos compatíveis com outras ferramentas de análise.
Esse sistema foi criado para resolver esses problemas. Pesquisadores, jornalistas e profissionais gastam horas transcrevendo áudio manualmente, além de enfrentar dificuldades para:

- **Localizar trechos específicos** em gravações longas
- **Identificar quem está falando** em conversas com múltiplos participantes
- **Exportar transcrições** em formatos compatíveis com diferentes ferramentas
- **Navegar rapidamente** entre o áudio e o texto transcrito

Este projeto automatiza todo esse processo, reduzindo drasticamente o tempo necessário e melhorando a qualidade da análise de conteúdo.

---

## 💡 Solução proposta

O **Transcritor de Entrevistas com Whisper e PyAnnote** oferece:

1. **Transcrição automática**: Utiliza o modelo Whisper (OpenAI) para converter áudio em texto com alta precisão
2. **Interface web interativa**: Player de vídeo sincronizado com segmentos de texto clicáveis
3. **Identificação de speakers**: Integração opcional com PyAnnote para diferenciar quem está falando
4. **Busca inteligente**: Filtragem em tempo real dos segmentos transcritos
5. **Exportação flexível**: Download em TXT, JSON e SRT para uso em outras ferramentas
6. **Navegação por timestamps**: Clique em qualquer segmento para pular direto no vídeo

---

## 🏗️ Arquitetura do sistema:

O projeto segue uma arquitetura cliente-servidor com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                       FRONTEND (Web)                        │
│  HTML + CSS + JavaScript → Interface de usuário             │
│  - Upload de arquivos                                       │
│  - Player de vídeo                                          │
│  - Lista de segmentos                                       │
│  - Busca e download                                         │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST API
┌──────────────────▼──────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  - Gerenciamento de uploads                                 │
│  - Roteamento de requisições                                │
│  - Servir arquivos estáticos                                │
│  - API REST para transcrições                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│               SERVIÇOS DE PROCESSAMENTO                     │
│                                                             │
│  ┌─────────────────┐         ┌──────────────────┐           │
│  │ TranscriptService│──────▶│ Whisper Model    │            │
│  │                  │        │ (OpenAI)         │           │
│  └────────┬─────────┘        └──────────────────┘           │
│           │                                                 │
│           │ (opcional)                                      │
│           ▼                                                 │
│  ┌──────────────────┐                                       │
│  │ PyAnnote Audio   │                                       │
│  │ (Diarization)    │                                       │
│  └──────────────────┘                                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  CAMADA DE DADOS                            │
│  - input/    → arquivos de vídeo/áudio originais            │
│  - output/   → transcrições em JSON/TXT/SRT                 │
│  - frontend/media/ → cópias para reprodução web             │
│  - logs/     → registros de execução                        │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de processamento é um pipeline sequencial em que cada etapa depende da anterior, como:

1. **Upload**: Usuário envia vídeo/áudio via interface web
2. **Armazenamento**: Arquivo salvo em `input/` e copiado para `frontend/media/`
3. **Transcrição**: Whisper processa o áudio e gera segmentos com timestamps
4. **Diarization** (opcional): PyAnnote identifica diferentes speakers
5. **Normalização**: Segmentos formatados em estrutura JSON padrão
6. **Exportação**: Geração automática de TXT, JSON e SRT
7. **Visualização**: Frontend renderiza player sincronizado com transcrição

---

## 🛠️ Tecnologias utilizadas:

Com relação às tecnologias, o projeto é construído com:

### Backend:

O backend é desenvolvido utilizando o framework **FastAPI**, que é conhecido por sua alta performance e facilidade de uso. Ele é responsável por gerenciar as rotas da API, processar os uploads de arquivos, interagir com o modelo de transcrição Whisper e, opcionalmente, com a biblioteca PyAnnote para diarization. O backend também lida com a geração dos arquivos de saída (TXT, JSON, SRT) e serve os arquivos estáticos para o frontend.

- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web moderno e assíncrono
- **Uvicorn** - Servidor ASGI de alta performance
- **OpenAI Whisper** - Modelo de transcrição de áudio para texto
- **PyAnnote.audio** (opcional) - Diarization e identificação de speakers
- **PyTorch** - Framework de deep learning (dependência do Whisper)
- **FFmpeg** - Processamento de áudio e vídeo

### Frontend:

Já o frontend é construído com tecnologias web tradicionais, utilizando HTML5 para a estrutura da página, CSS3 para a estilização (incluindo um tema escuro) e JavaScript vanilla para a lógica de interação. Ele se comunica com o backend através de requisições HTTP para enviar arquivos, receber transcrições e controlar a reprodução do vídeo.

- **HTML5** - Estrutura
- **CSS3** - Estilização moderna com dark theme
- **JavaScript (Vanilla)** - Lógica de interação

### Ferramentas de desenvolvimento:

As ferramentas utilizadas para o desenvolvimento incluem:

- **Python Logging** - Sistema de logs estruturado
- **Python Multipart** - Upload de arquivos
- **JSON** - Formato de troca de dados

---

## 📁 Estrutura de diretórios:

A organização do projeto é estruturada para facilitar a manutenção e escalabilidade, com separação clara entre frontend, backend, serviços de processamento e dados:

```
Transcritor-de-Entrevistas/
│
├── docs/                          # Documentação técnica
│   ├── architecture.md            # Arquitetura detalhada
│   ├── como_funciona.md           # Fluxo de funcionamento
│   ├── diarization.md             # Guia de identificação de speakers
│   └── roadmap.md                 # Melhorias futuras
│
├── frontend/                      # Interface web
│   ├── index.html                 # Página principal
│   ├── style.css                  # Estilos da aplicação
│   ├── app.js                     # Lógica do frontend
│   └── media/                     # Vídeos para reprodução web
│
├── input/                         # Arquivos de entrada (vídeos/áudios)
├── output/                        # Transcrições geradas (JSON/TXT/SRT)
├── logs/                          # Logs de execução
├── samples/                       # Arquivos de exemplo
│
├── src/                           # Código-fonte principal
│   ├── __init__.py
│   ├── api.py                     # Rotas da API REST
│   ├── cleaner.py                 # Limpeza de segmentos
│   ├── cli.py                     # Interface de linha de comando
│   ├── config.py                  # Configurações globais
│   ├── exporter.py                # Exportação de arquivos
│   ├── formatter.py               # Formatação de saídas
│   ├── logger.py                  # Sistema de logging
│   ├── metadata.py                # Metadados das transcrições
│   ├── transcriber.py             # Integração com Whisper
│   ├── utils.py                   # Funções auxiliares
│   │
│   └── services/                  # Camada de serviços
│       ├── __init__.py
│       └── transcript_service.py  # Lógica de processamento
│
├── tests/                         # Testes automatizados
│   ├── __init__.py
│   └── test_utils.py
│
├── main.py                        # Ponto de entrada da aplicação
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

---

## 🚀 Como executar o projeto:

Abaixo estão as instruções passo a passo para configurar e rodar o projeto localmente:

### Pré-requisitos:

Para rodar o projeto localmente, certifique-se de ter:

- **Python 3.11+** instalado
- **FFmpeg** instalado no sistema
- **Git** para clonar o repositório

### 1. Clone o repositório

```bash
git clone https://github.com/Victorkaue333/whisper-interview-transcriber.git
cd whisper-interview-transcriber
```

### 2. Crie e ative um ambiente virtual

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### 4. Instale o FFmpeg (se ainda não tiver)

**Windows:**

1. Baixe o FFmpeg em [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extraia e adicione ao PATH do sistema

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

### 5. Inicie o servidor

```bash
uvicorn src.api:app --reload
```

### 6. Acesse a aplicação

Abra o navegador e acesse:

```
http://127.0.0.1:8000
```

---

## 🔄 Fluxo de funcionamento do sistema:

O fluxo de funcionamento do sistema é o seguinte:

### Processo completo de transcrição

```
1. UPLOAD
   ↓
   Usuário seleciona arquivo de vídeo/áudio na interface
   Opcionalmente marca "Identificar quem está falando"
   
2. RECEBIMENTO
   ↓
   FastAPI recebe arquivo via POST /api/upload
   Valida formato (.mp4, .mov, .avi, .mp3, .wav, etc.)
   
3. ARMAZENAMENTO
   ↓
   Gera ID único (job_id)
   Salva arquivo em input/{job_id}_{filename}
   Copia para frontend/media/ (para reprodução web)
   
4. TRANSCRIÇÃO
   ↓
   Carrega modelo Whisper (base/small/medium/large)
   Processa áudio completo
   Gera segmentos com timestamps (start, end, text)
   
5. DIARIZATION (opcional)
   ↓
   Se habilitado, carrega PyAnnote Pipeline
   Identifica diferentes vozes no áudio
   Atribui labels (SPEAKER_00, SPEAKER_01, etc.)
   Mapeia speakers para segmentos
   
6. NORMALIZAÇÃO
   ↓
   Converte resultado Whisper para formato padrão:
   {
     "start": 0.0,
     "end": 5.2,
     "speaker": "SPEAKER_00",
     "text": "Olá, tudo bem?"
   }
   
7. EXPORTAÇÃO
   ↓
   Gera automaticamente:
   - {job_id}_segments.json → dados completos
   - {job_id}.txt → transcrição formatada
   - {job_id}.srt → legendas para vídeo
   
8. RESPOSTA
   ↓
   Retorna JSON com:
   - job_id
   - video_url (para player)
   - segments[] (lista de transcrições)
   
9. RENDERIZAÇÃO
   ↓
   Frontend recebe dados
   Carrega vídeo no player
   Renderiza lista de segmentos clicáveis
   Habilita busca e downloads
   
10. INTERAÇÃO
    ↓
    Usuário clica em segmento → vídeo pula para timestamp
    Usuário busca palavra → filtra segmentos
    Usuário clica download → baixa TXT/JSON/SRT
```

---

## 👨‍💻 Autor:

Aqui estão minhas informações de contato e links para meus perfis profissionais:

**Victor Alves** - [GitHub](https://github.com/Victorkaue333)
**LinkedIn** - [Victor Alves](https://www.linkedin.com/in/victor-kauê)
**Portfólio** - [victorkauê](https://victorkaue.netlify.app/)