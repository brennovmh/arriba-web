# API

## Usuário

- `POST /auth/login`
- `GET /auth/me`
- `GET /analyses`
- `POST /analyses`
- `GET /analyses/{id}`
- `POST /analyses/{id}/upload`
- `POST /analyses/{id}/submit`
- `POST /analyses/{id}/reprocess`
- `GET /jobs/{id}`
- `GET /jobs/{id}/logs`
- `GET /jobs/{id}/results`
- `POST /jobs/{id}/cancel`
- `GET /pipelines`
- `GET /files/{id}/download`

## Worker

- `POST /workers/register` admin only
- `POST /worker/poll`
- `POST /worker/heartbeat`
- `POST /worker/jobs/{id}/claim`
- `GET /worker/jobs/{id}/bundle`
- `GET /worker/files/{id}/download`
- `POST /worker/jobs/{id}/status`
- `POST /worker/jobs/{id}/logs`
- `POST /worker/jobs/{id}/results`

## Observações

- Usuários usam JWT Bearer no header `Authorization`.
- Worker usa `X-Worker-Token`.
- Swagger fica em `/docs`.
