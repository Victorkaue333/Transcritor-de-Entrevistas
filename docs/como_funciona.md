### Fluxo completo:

Usuário envia vídeo
        ↓
FastAPI recebe arquivo
        ↓
Salva em input/
        ↓
Roda transcrição com Whisper
        ↓
Gera segmentos em JSON
        ↓
Frontend recebe JSON
        ↓
Renderiza player + lista
        ↓
Usuário clica em um trecho
        ↓
Vídeo pula para o timestamp