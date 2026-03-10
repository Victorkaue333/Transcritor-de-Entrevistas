# Identificação de Speakers (Diarization)

## O que é?

O recurso de diarization permite que o sistema identifique **quem está falando** em cada segmento da transcrição. Isso é especialmente útil para entrevistas com múltiplas pessoas.

## Como habilitar

### 1. Instalar dependências

```bash
pip install pyannote.audio
```

### 2. Configurar HuggingFace Token

1. Crie uma conta em [HuggingFace](https://huggingface.co)
2. Aceite os termos de uso em: https://huggingface.co/pyannote/speaker-diarization-3.1
3. Gere um token de acesso em: https://huggingface.co/settings/tokens
4. Faça login no CLI:

```bash
huggingface-cli login
```

Ou configure como variável de ambiente:

**Windows:**
```bash
set HF_TOKEN=seu_token_aqui
```

**Linux/macOS:**
```bash
export HF_TOKEN=seu_token_aqui
```

### 3. Usar na interface

Na interface web, marque a opção **"Identificar quem está falando"** antes de fazer upload do arquivo.

## Como funciona

O sistema usa o modelo **pyannote/speaker-diarization-3.1** que:

1. Analisa o áudio e identifica diferentes vozes
2. Atribui um label (SPEAKER_00, SPEAKER_01, etc.) para cada voz detectada
3. Mapeia esses labels para os segmentos transcritos pelo Whisper

## Limitações

- O processamento fica **mais lento** (pode demorar 2-3x mais)
- Na primeira vez, o modelo será baixado (~1GB)
- Funciona melhor com áudio de boa qualidade
- Não identifica **nomes** das pessoas, apenas diferencia vozes

## Se não configurar

Se você **NÃO** instalar pyannote.audio ou não configurar o token:
- A opção ainda aparecerá na interface
- Mas todos os segmentos terão speaker como "Desconhecido"
- O sistema funcionará normalmente, apenas sem identificação de speakers
