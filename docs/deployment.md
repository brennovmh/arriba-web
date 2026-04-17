# Deployment

## VPS

1. Ajuste `backend/.env` e `frontend/.env`.
2. Suba PostgreSQL, backend e frontend com `docker compose up -d --build`.
3. Garanta persistência do volume `platform_storage`.
4. Proteja a VPS com HTTPS via reverse proxy externo se exposta para fora da rede interna.

## Backend

- Porta padrão: `8000`
- Swagger: `/docs`
- Storage local inicial em `/data/platform_storage`

## Frontend

- Porta padrão: `5173`
- `VITE_API_BASE_URL` deve apontar para o backend publicado na VPS

## Banco

- PostgreSQL 16
- Para evoluir, substituir `Base.metadata.create_all` por migrações Alembic aplicadas explicitamente no deploy
