# Como Funciona o Sistema?:

## 🎬 Fluxo Completo do Usuário

O fluxo do usuário é projetado para ser simples e intuitivo, mesmo para quem não tem experiência técnica. Aqui está o passo a passo:

```
1. Usuário acessa a interface web
        ↓
2. Seleciona arquivo de vídeo/áudio
        ↓
3. (Opcional) Marca "Identificar quem está falando"
        ↓
4. Clica em "Processar Vídeo"
        ↓
5. Sistema processa (pode demorar alguns minutos)
        ↓
6. Interface exibe:
   • Vídeo tocando no player
   • Lista de segmentos transcritos com timestamps
   • Destaque automático do segmento em reprodução
        ↓
7. Usuário pode:
   • Clicar em segmentos para pular no vídeo
   • Buscar palavras-chave
   • Baixar transcrição (TXT, JSON, SRT)
        ↓
8. Dados salvos no navegador (persiste após reload)
```

---

## 🔄 Processo Técnico Detalhado

### Fase 1: Upload e Preparação

**O que acontece:**
1. Frontend envia arquivo via FormData (multipart/form-data)
2. Backend gera um **job_id único** usando UUID
3. Arquivo salvo em duas localizações:
   - `input/{job_id}.{extensão}` → arquivo original
   - `frontend/media/{job_id}.{extensão}` → cópia para o player

**Código responsável:**
- Frontend: `app.js` → função no evento `uploadBtn.addEventListener("click")`
- Backend: `src/api.py` → endpoint `POST /api/upload`
- Service: `src/services/transcript_service.py` → método `process_video()`

**Exemplo de job_id:**
```
Original: minha_entrevista.mp4
Job ID gerado: a7f3c2e1
Salvo como: 
  - input/a7f3c2e1.mp4
  - frontend/media/a7f3c2e1.mp4
```

---

### Fase 2: Transcrição com Whisper

**O que acontece:**
1. Carrega modelo Whisper **small** (~466 MB)
2. Processa o áudio extraindo:
   - Texto transcrito
   - Timestamp inicial (start)
   - Timestamp final (end)
3. Gera uma lista de segmentos

**Código responsável:**
- Service: `src/services/transcript_service.py` → método `_run_existing_transcriber()`
- Core: `src/transcriber.py` → função `transcribe_file()`

**Exemplo de saída do Whisper:**
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Olá, meu nome é João."
    },
    {
      "start": 3.5,
      "end": 7.2,
      "text": "Hoje vamos falar sobre tecnologia."
    }
  ]
}
```

**Tempo de processamento:**
- Vídeo de 10 minutos → ~2-5 minutos de processamento
- Depende do hardware (GPU acelera muito)
- Modelo small: balanceado entre velocidade e precisão

---

### Fase 3: Identificação de Speakers (Opcional)

**O que acontece:**
1. Se diarization estiver habilitado, usa PyAnnote
2. Analisa frequências de voz no áudio
3. Cria clusters de vozes similares
4. Atribui labels: SPEAKER_00, SPEAKER_01, etc.
5. Mapeia timestamps do Whisper para speakers

**Código responsável:**
- Service: `src/services/transcript_service.py` → método `_apply_diarization()`

**Antes da diarização:**
```json
{
  "start": 0.0,
  "end": 3.5,
  "text": "Olá, meu nome é João.",
  "speaker": "Desconhecido"
}
```

**Depois da diarização:**
```json
{
  "start": 0.0,
  "end": 3.5,
  "text": "Olá, meu nome é João.",
  "speaker": "SPEAKER_00"
}
```

**Limitações:**
- Não identifica nomes reais (apenas diferencia vozes)
- Adiciona 2-3x ao tempo de processamento
- Requer configuração de token HuggingFace

---

### Fase 4: Geração de Arquivos de Download

**O que acontece:**
1. Cria `{job_id}_segments.json` com dados completos
2. Gera `{job_id}.txt` formatado para leitura
3. Gera `{job_id}.srt` para uso em editores de vídeo

**Código responsável:**
- Service: `src/services/transcript_service.py` → método `_generate_download_files()`

**Formato TXT:**
```
[00:00 --> 00:03] SPEAKER_00
Olá, meu nome é João.

[00:03 --> 00:07] SPEAKER_01
Prazer, João. Como você está?

[00:07 --> 00:12] SPEAKER_00
Estou bem, obrigado por perguntar.
```

**Formato SRT (legendas):**
```
1
00:00:00,000 --> 00:00:03,500
Olá, meu nome é João.

2
00:00:03,500 --> 00:00:07,200
Prazer, João. Como você está?

3
00:00:07,200 --> 00:00:12,000
Estou bem, obrigado por perguntar.
```

**Formato JSON:**
```json
[
  {
    "start": 0.0,
    "end": 3.5,
    "text": "Olá, meu nome é João.",
    "speaker": "SPEAKER_00"
  }
]
```

---

### Fase 5: Retorno ao Frontend

**O que acontece:**
1. Backend envia resposta JSON com:
   - job_id
   - URL do vídeo
   - Lista de segmentos
2. Frontend renderiza interface
3. Dados salvos no localStorage

**Código responsável:**
- Backend: `src/api.py` → retorno do endpoint `/api/upload`
- Frontend: `app.js` → função `renderSegments()`

**Response da API:**
```json
{
  "job_id": "a7f3c2e1",
  "video_url": "/media/a7f3c2e1.mp4",
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Olá, meu nome é João.",
      "speaker": "SPEAKER_00"
    }
  ],
  "message": "Transcrição concluída com sucesso"
}
```

---

## 🎯 Sincronização Vídeo ↔ Texto

### Como funciona o destaque automático

**Mecanismo:**
1. Evento `timeupdate` do player HTML5 dispara a cada ~250ms
2. JavaScript pega o tempo atual do vídeo (ex: 5.2 segundos)
3. Compara com os timestamps de cada segmento:
   ```javascript
   if (currentTime >= segment.start && currentTime <= segment.end) {
     // Este é o segmento ativo!
   }
   ```
4. Adiciona classe CSS `.active` ao segmento correspondente
5. Faz scroll automático para centralizar na tela

**Código responsável:**
- Frontend: `app.js` → evento `videoPlayer.addEventListener("timeupdate")`

**Efeito visual:**
- Ícone ▶ azul na lateral
- Background azul claro
- Borda destacada
- Texto mais claro
- Scroll suave automático

---

## 🔍 Sistema de Busca

**Funcionamento:**
1. Usuário digita no campo de busca
2. Evento `input` captura cada tecla pressionada
3. Filtra segmentos que contêm a palavra (case-insensitive)
4. Re-renderiza lista apenas com resultados

**Código responsável:**
- Frontend: `app.js` → `searchInput.addEventListener("input")`

**Exemplo:**
```
Busca: "tecnologia"
        ↓
Filtra segmentos onde text.includes("tecnologia")
        ↓
Exibe apenas segmentos relevantes
```

---

## 💾 Persistência de Dados

### Como funciona o localStorage

**Quando salva:**
- Após transcrição completa
- Ao clicar em segmentos
- Automático (não precisa de ação do usuário)

**O que salva:**
```javascript
{
  jobId: "a7f3c2e1",
  segments: [...], // todos os segmentos
  videoUrl: "/media/a7f3c2e1.mp4"
}
```

**Quando carrega:**
- Automaticamente ao recarregar a página
- Restaura vídeo, transcrição e botões de download

**Código responsável:**
- Frontend: `app.js` → funções `saveToLocalStorage()` e `loadFromLocalStorage()`

**Por que isso é útil:**
- ✅ Não perde transcrição ao dar F5
- ✅ Pode fechar aba e voltar depois
- ✅ Funciona offline (depois de processado)

---

## 📊 Sistema de Logs

### Logs Visuais (Frontend)

**Tipos de log:**
- **INFO** (azul): Eventos normais
- **SUCCESS** (verde): Operações concluídas
- **WARNING** (amarelo): Avisos não-críticos
- **ERROR** (vermelho): Erros que precisam atenção

**Exemplo de logs durante upload:**
```
[16:23:45] [INFO] Arquivo selecionado: entrevista.mp4 (45.2 MB)
[16:23:46] [INFO] Enviando arquivo para o servidor...
[16:23:47] [INFO] Aguardando processamento (isso pode demorar alguns minutos)...
[16:28:12] [SUCCESS] Transcrição concluída! Job ID: a7f3c2e1
[16:28:12] [SUCCESS] 123 segmentos gerados
[16:28:12] [INFO] Arquivos de download prontos (TXT, JSON, SRT)
```

### Logs do Backend (Python)

**Armazenamento:**
- Diretório: `logs/`
- Formato: texto com timestamps

**Código responsável:**
- Core: `src/logger.py` → classe `Logger`

---

## ⚙️ Configurações e Modelos

### Modelos Whisper Disponíveis

| Modelo | Tamanho | Velocidade | Precisão | Recomendado para |
|--------|---------|------------|----------|------------------|
| tiny   | 39 MB   | Muito rápida | ~60% | Testes rápidos |
| base   | 74 MB   | Rápida     | ~75% | Rascunhos |
| **small** | **466 MB** | **Média** | **~84%** | **Padrão (atual)** |
| medium | 1.5 GB  | Lenta      | ~92% | Alta precisão |
| large  | 2.9 GB  | Muito lenta | ~98% | Máxima qualidade |

**Como alterar:**
- Arquivo: `src/config.py`
- Variável: `DEFAULT_MODEL = "small"`

---

## 🎨 Como a Interface Funciona

### Componentes da Interface

1. **Painel de Logs** (topo)
   - Mostra feedback em tempo real
   - Auto-scroll para última mensagem
   - Botão "Limpar" para resetar

2. **Área de Upload** (esquerda superior)
   - Input de arquivo
   - Checkbox de diarization
   - Botão de processamento

3. **Player de Vídeo** (esquerda)
   - HTML5 video player nativo
   - Controles padrão do navegador
   - Auto-play ao clicar em segmento

4. **Painel de Transcrição** (direita)
   - Campo de busca
   - Botões de download (TXT/JSON/SRT)
   - Lista scrollável de segmentos
   - Destaque automático do segmento ativo

### Responsividade

- Desktop: Layout em 2 colunas (player | transcrição)
- Mobile/Tablet: Layout em 1 coluna (vertical)

---

## 🚀 Otimizações Implementadas

### Performance

1. **Sincronização inteligente**
   - Só atualiza quando muda de segmento
   - Evita re-renderizações desnecessárias

2. **Search otimizado**
   - Filtragem em memória (sem requisições)
   - Case-insensitive nativo do JavaScript

3. **Scroll suave**
   - `behavior: "smooth"` do CSS
   - Centraliza segmento ativo

### UX (Experiência do Usuário)

1. **Feedback visual constante**
   - Logs em tempo real
   - Animações suaves
   - Dark theme para conforto visual

2. **Persistência automática**
   - LocalStorage transparente
   - Não perde dados no reload

3. **Navegação intuitiva**
   - Clique direto nos segmentos
   - Busca instantânea
   - Download com 1 clique

---

## 🐛 Tratamento de Erros

### Frontend

**Erros capturados:**
- Arquivo não selecionado
- Erro de rede durante upload
- Resposta inválida da API

**Como trata:**
```javascript
try {
  const response = await fetch("/api/upload", {...});
  // processa resposta
} catch (error) {
  addLog("error", `Erro ao processar: ${error.message}`);
  statusText.textContent = `Erro: ${error.message}`;
}
```

### Backend

**Erros capturados:**
- Arquivo corrompido
- Modelo não encontrado
- Erro durante transcrição
- Disco cheio

**Como trata:**
```python
try:
    result = transcribe_file(file_path)
except Exception as e:
    logger.error(f"Erro na transcrição: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

---

## 📝 Formatos Suportados

### Entrada (Upload)

**Vídeo:**
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

**Áudio:**
- `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### Saída (Download)

**TXT:**
- Transcrição formatada para leitura humana
- Inclui timestamps e speakers
- Encoding: UTF-8

**JSON:**
- Dados brutos estruturados
- Fácil de processar programaticamente
- Inclui todos os metadados

**SRT:**
- Formato padrão de legendas
- Compatível com editores de vídeo
- Numeração sequencial automática

---

## 🔐 Privacidade e Segurança

### Dados do Usuário

- ✅ **Tudo processado localmente** (não envia para nuvem externa)
- ✅ Arquivos armazenados apenas no servidor
- ✅ Sem coleta de dados pessoais
- ⚠️ localStorage exposto no navegador

### Limitações Atuais

- ⚠️ Sem autenticação de usuários
- ⚠️ Arquivos visíveis para quem tem acesso ao servidor
- ⚠️ Sem criptografia de arquivos

---

## 💡 Dicas de Uso

### Para melhores resultados:

1. **Áudio de qualidade**
   - Use microfone decente
   - Evite ruído de fundo
   - Ambiente fechado é melhor

2. **Idioma**
   - Sistema configurado para Português
   - Funciona melhor com o idioma configurado

3. **Duração**
   - Vídeos curtos processam mais rápido
   - Para vídeos longos (>1h), seja paciente

4. **Diarization**
   - Use apenas se realmente precisa identificar speakers
   - Dobra/triplica o tempo de processamento
   - Funciona melhor com 2-3 pessoas (não funciona bem com muitas vozes)

---

Este documento deve ajudar a entender completamente como o sistema opera, desde a interface até o processamento interno!