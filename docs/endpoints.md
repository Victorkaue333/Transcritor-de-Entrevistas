### API Endpoints:

Abaixo estão os principais endpoints da API REST:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Retorna página HTML principal |
| `POST` | `/api/upload` | Upload e processamento de vídeo |
| `GET` | `/api/transcript/{job_id}` | Retorna transcrição por ID |
| `GET` | `/api/download/{job_id}/{format}` | Download em TXT/JSON/SRT |