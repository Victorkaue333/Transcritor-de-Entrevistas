# Arquitetura do Sistema

## Visão Geral

O **Whisper Interview Transcriber** é uma aplicação web full-stack que processa vídeos/áudios usando Inteligência Artificial para gerar transcrições navegáveis. A arquitetura segue o padrão **cliente-servidor** com separação clara entre camadas.

---

## 🏗️ Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
│                       (Frontend Web)                         │
├─────────────────────────────────────────────────────────────┤
│  • HTML5 + CSS3 + Vanilla JavaScript                        │
│  • Sem frameworks (React/Vue)                               │
│  • Responsivo e dark theme                                  │
│                                                             │
│  Componentes principais:                                    │
│  ├─ Upload Form (file input + diarization checkbox)        │
│  ├─ Video Player (HTML5 <video>)                           │
│  ├─ Transcript List (segmentos clicáveis)                  │
│  ├─ Search Bar (filtro em tempo real)                      │
│  ├─ Download Buttons (TXT/JSON/SRT)                        │
│  └─ Logs Panel (feedback visual)                           │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP REST API
                   │ (JSON)
┌──────────────────▼──────────────────────────────────────────┐
│                     CAMADA DE API                           │
│                    (FastAPI + Uvicorn)                       │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                 │
│  • POST /api/upload                                         │
│    ├─ Recebe arquivo multipart/form-data                   │
│    ├─ Parâmetros: file, enable_diarization                 │
│    └─ Retorna: job_id, segments[], video_url               │
│                                                             │
│  • GET /api/download/{job_id}/{format}                     │
│    ├─ Formatos: txt, json, srt                             │
│    └─ Retorna: arquivo para download                       │
│                                                             │
│  • StaticFiles mount                                        │
│    ├─ /frontend → interface web                            │
│    └─ /media → vídeos processados                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  CAMADA DE NEGÓCIOS                         │
│                 (Services + Transcriber)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │          TranscriptService (Orquestrador)             │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │  Responsabilidades:                                    │ │
│  │  • Gerenciar job IDs (UUID)                           │ │
│  │  • Copiar arquivos entre diretórios                   │ │
│  │  • Orquestrar processamento em 5 fases                │ │
│  │  • Aplicar diarização (opcional)                      │ │
│  │  • Gerar arquivos de saída (JSON/TXT/SRT)            │ │
│  │                                                        │ │
│  │  Fases de processamento:                              │ │
│  │  1️⃣  Preparação (salvar arquivo)                       │ │
│  │  2️⃣  Transcrição (Whisper)                             │ │
│  │  3️⃣  Diarização (PyAnnote - opcional)                  │ │
│  │  4️⃣  Geração de arquivos (TXT/SRT)                     │ │
│  │  5️⃣  Finalização (logs e retorno)                      │ │
│  └───────────────┬───────────────────────────────────────┘ │
│                  │                                         │
│  ┌───────────────▼───────────────────────────────────────┐ │
│  │              Transcriber (Whisper)                    │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │  • Biblioteca: openai-whisper                         │ │
│  │  • Modelo padrão: small (~466 MB)                     │ │
│  │  • Idioma: Português (pt)                             │ │
│  │  • Output: segments com text, start, end              │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       PyAnnote Audio (Diarização - Opcional)        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  • Modelo: pyannote/speaker-diarization-3.1         │   │
│  │  • Identifica SPEAKER_00, SPEAKER_01, etc.          │   │
│  │  • Requer token HuggingFace                         │   │
│  │  • Se não instalado: todos = "Desconhecido"         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  CAMADA DE PERSISTÊNCIA                     │
│                   (Sistema de Arquivos)                      │
├─────────────────────────────────────────────────────────────┤
│  📁 input/                                                  │
│     └─ Arquivos originais de vídeo/áudio                   │
│                                                             │
│  📁 output/                                                 │
│     ├─ {job_id}_segments.json (dados completos)            │
│     ├─ {job_id}.txt (transcrição formatada)                │
│     └─ {job_id}.srt (legendas)                             │
│                                                             │
│  📁 frontend/media/                                         │
│     └─ Cópias dos vídeos para playback web                 │
│                                                             │
│  📁 logs/                                                   │
│     └─ Registros de execução e erros                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados Completo

### 1️⃣ Upload e Preparação

No processo de upload, o usuário seleciona um arquivo e escolhe se deseja habilitar a diarização. O frontend envia uma requisição POST para a API, que gera um `job_id` único e salva o arquivo na pasta `input/`. Em seguida, o arquivo é copiado para `frontend/media/` para ser acessível pelo player.

```
Usuário seleciona arquivo
        ↓
[Frontend] FormData com file + enable_diarization
        ↓
[API] POST /api/upload
        ↓
[TranscriptService] Gera job_id (UUID)
        ↓
Salva em input/{job_id}{ext}
        ↓
Copia para frontend/media/{job_id}{ext}
```

### 2️⃣ Transcrição com Whisper

Já com o arquivo salvo, o `TranscriptService` chama o `Transcriber` para processar o áudio. O modelo Whisper é carregado (se ainda não estiver em cache) e o áudio é transcrito, retornando uma lista de segmentos com texto e timestamps.

```
[TranscriptService] Chama _run_existing_transcriber()
        ↓
[Transcriber] Carrega modelo small
        ↓
Processa áudio (pode demorar minutos)
        ↓
Retorna: {
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Olá, como vai?"
    }
  ]
}
```

### 3️⃣ Diarização (se habilitada)

O sistema verifica se a diarização foi solicitada. Se sim, ele chama o modelo PyAnnote para analisar o áudio e identificar os diferentes falantes. Os segmentos são atualizados com um campo adicional `speaker`.

```
[TranscriptService] _apply_diarization()
        ↓
[PyAnnote] Analisa vozes no áudio
        ↓
Mapeia timestamps → speakers
        ↓
Atualiza segments:
{
  "start": 0.0,
  "end": 3.5,
  "text": "Olá, como vai?",
  "speaker": "SPEAKER_00"  ← adicionado
}
```

### 4️⃣ Geração de Arquivos

```
[TranscriptService] _generate_download_files()
        ↓
Gera output/{job_id}.txt (formato legível)
        ↓
Gera output/{job_id}.srt (legendas padrão)
        ↓
Salva output/{job_id}_segments.json
```

### 5️⃣ Retorno ao Cliente

```
[API] Retorna JSON:
{
  "job_id": "a1b2c3d4",
  "video_url": "/media/a1b2c3d4.mp4",
  "segments": [...],
  "message": "Transcrição concluída"
}
        ↓
[Frontend] Renderiza player + lista
        ↓
Salva em localStorage para persistência
```

---

## 🧩 Módulos e Responsabilidades

### Frontend (`frontend/`)

| Arquivo | Responsabilidade |
|---------|------------------|
| `index.html` | Estrutura da interface (player, lista, logs) |
| `style.css` | Estilização dark theme e layout responsivo |
| `app.js` | Lógica de upload, sincronização vídeo/texto, localStorage |

**Tecnologias:**
- HTML5 Video API
- Fetch API para requisições HTTP
- localStorage para persistência entre reloads
- Event listeners para sincronização timeupdate

### Backend (`src/`)

#### API Layer
- **`api.py`**: Endpoints FastAPI, middleware CORS, static files

#### Business Logic
- **`services/transcript_service.py`**: Orquestrador principal de processamento
- **`transcriber.py`**: Wrapper do Whisper com configurações customizadas

#### Utilities
- **`config.py`**: Constantes globais (diretórios, modelo padrão)
- **`logger.py`**: Sistema de logs com timestamps
- **`metadata.py`**: Verificação de formatos de arquivo
- **`exporter.py`**: Conversão de formatos (JSON → SRT, TXT)
- **`formatter.py`**: Formatação de texto e timestamps
- **`cleaner.py`**: Sanitização de nomes de arquivos

---

## 🔐 Segurança e Validações

### Upload de Arquivos
- ✅ Validação de extensões permitidas (`.mp4`, `.mp3`, `.wav`, etc.)
- ✅ Sanitização de nomes de arquivos (remove caracteres especiais)
- ✅ Geração de UUIDs únicos para evitar colisões
- ⚠️ **TODO**: Limite de tamanho de arquivo (atualmente ilimitado)

### API
- ✅ CORS habilitado para desenvolvimento local
- ✅ Error handling com try/catch
- ⚠️ **TODO**: Rate limiting para uploads
- ⚠️ **TODO**: Autenticação de usuários

---

## ⚡ Performance e Otimizações

### Gargalos Identificados
1. **Transcrição com Whisper**: Processo mais lento (minutos para vídeos longos)
2. **Diarização**: Adiciona 2-3x ao tempo de processamento
3. **Cópia de arquivos**: Vídeos grandes consomem espaço duplicado

### Otimizações Implementadas
- ✅ Logs em tempo real para feedback do usuário
- ✅ Sincronização eficiente (só atualiza ao mudar de segmento)
- ✅ Modelo `small` por padrão (balanceado)

### Melhorias Futuras
- 🔄 Processamento assíncrono com filas (Celery/RQ)
- 🔄 Cache de modelos em memória
- 🔄 Compressão de vídeos antes de salvar
- 🔄 WebSocket para progress bars em tempo real

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11+**
- **FastAPI**: Framework web assíncrono
- **Uvicorn**: Servidor ASGI de alta performance
- **OpenAI Whisper**: Modelo de transcrição (small - 466MB)
- **PyAnnote.audio**: Diarização de speakers (opcional)
- **Pydantic**: Validação de dados

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Grid, Flexbox, variáveis CSS
- **JavaScript ES6+**: Async/await, fetch, classes
- **LocalStorage API**: Persistência de dados

### Infraestrutura
- **Sistema de arquivos local**: Persistência simples
- **Logging nativo do Python**: Debug e monitoramento

---

## 📦 Estrutura de Diretórios

```
whisper-interview-transcriber/
│
├── frontend/                    # Interface web
│   ├── index.html              # Página principal
│   ├── style.css               # Estilos
│   ├── app.js                  # Lógica do frontend
│   └── media/                  # Vídeos para playback
│
├── src/                        # Backend Python
│   ├── api.py                  # FastAPI routes
│   ├── config.py               # Configurações globais
│   ├── transcriber.py          # Wrapper do Whisper
│   ├── cli.py                  # Interface de linha de comando
│   ├── logger.py               # Sistema de logs
│   ├── metadata.py             # Validação de arquivos
│   ├── exporter.py             # Exportação de formatos
│   ├── formatter.py            # Formatação de texto
│   ├── cleaner.py              # Sanitização
│   └── services/
│       └── transcript_service.py  # Orquestrador principal
│
├── input/                      # Arquivos originais
├── output/                     # Transcrições geradas
├── logs/                       # Logs do sistema
├── docs/                       # Documentação
│
├── requirements.txt            # Dependências Python
├── main.py                     # Entry point do servidor
└── README.md                   # Documentação principal
```

---

## 🔌 Integrações Externas

### OpenAI Whisper
- **Tipo**: Biblioteca Python local
- **Requisito**: Modelo baixado automaticamente na primeira execução
- **Sem necessidade de API key**

### HuggingFace (PyAnnote)
- **Tipo**: Modelo online com token de autenticação
- **Requisito**: Conta HuggingFace + aceitar termos de uso
- **Opcional**: Sistema funciona sem diarização

---

## 📊 Modelo de Dados

### Segment (estrutura principal)

```json
{
  "start": 0.0,           // float - timestamp inicial (segundos)
  "end": 3.5,             // float - timestamp final
  "text": "Olá mundo",    // string - texto transcrito
  "speaker": "SPEAKER_00" // string - identificador do falante (opcional)
}
```

### Response da API (/api/upload)

```json
{
  "job_id": "a1b2c3d4",
  "video_url": "/media/a1b2c3d4.mp4",
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Olá mundo",
      "speaker": "SPEAKER_00"
    }
  ],
  "message": "Transcrição concluída com sucesso"
}
```

---

## 🚀 Deploy e Escalabilidade

### Ambiente de Desenvolvimento
```bash
uvicorn src.api:app --reload
# Acesse: http://127.0.0.1:8000
```

### Ambiente de Produção
- **Servidor**: Uvicorn com múltiplos workers
- **Proxy reverso**: Nginx recomendado
- **Storage**: Volume persistente para input/output/media
- **Considerações**: GPU acelera Whisper significativamente

### Limitações Atuais
- ⚠️ Processos síncronos (bloqueia durante transcrição)
- ⚠️ Sem fila de jobs (um processamento por vez)
- ⚠️ Armazenamento local (não escalável para múltiplos servidores)

### Melhorias para Produção
- Migrar para arquitetura de microserviços
- Usar banco de dados (PostgreSQL) ao invés de arquivos
- Implementar fila de jobs (Redis + Celery)
- Adicionar CDN para servir vídeos
- Implementar autenticação JWT
- Monitoramento com Prometheus + Grafana
