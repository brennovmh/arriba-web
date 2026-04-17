# Lab NGS Platform MVP

Plataforma web MVP para uso interno em laboratório, com VPS como camada pública de entrada e uma workstation Linux atuando como worker remoto para execução local das pipelines via Docker.

## Stack escolhida

- Backend: `FastAPI + SQLAlchemy + PostgreSQL`
  Motivo: API rápida de implementar, tipagem simples, documentação automática e boa manutenção para um MVP interno.
- Frontend: `React + Vite + TypeScript`
  Motivo: setup enxuto, ciclo de desenvolvimento rápido e interface suficiente para dashboard, upload e acompanhamento.
- Worker: `Python + requests + subprocess`
  Motivo: fácil integração com Linux, Docker, diretórios locais e automação operacional da workstation.

## Estrutura

```text
platform/
  backend/
  frontend/
  worker/
  docs/
  docker-compose.yml
  README.md
```

## Fluxo

1. Usuário faz login no frontend.
2. Cria uma análise e envia FASTQs.
3. O backend grava metadados, armazena uploads na VPS e cria um job pendente.
4. O worker faz polling na API, faz claim do job, baixa os FASTQs e executa a pipeline dummy local via Docker.
5. O worker envia logs, status e resultados finais para a VPS.
6. O frontend exibe status, logs e outputs para download e preview.

## Subida local

```bash
cd /root/arriba-web/platform
docker compose up --build
```

Acesse:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/docs`

Credenciais iniciais:

- `admin@lab.local`
- `admin123`

Pipelines registradas no MVP:

- `dummy-ngs`
- `dummy-ngs-report`

## Executar o worker na workstation

1. Copie `worker/.env.example` para `worker/.env` e preencha `API_BASE_URL`, `WORKER_TOKEN` e `REFS_DIR`.
2. Construa a imagem da pipeline dummy:

```bash
cd /root/arriba-web/platform/worker/dummy_pipeline
docker build -t lab-ngs-dummy:latest .
```

3. Instale dependências do worker e rode:

```bash
cd /root/arriba-web/platform/worker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Registrar um worker

Faça login como admin e use o endpoint `POST /workers/register`.

Exemplo:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@lab.local","password":"admin123"}'
```

```bash
curl -X POST http://localhost:8000/workers/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_ADMIN>" \
  -d '{"name":"lab-workstation-01","capabilities_json":{"pipelines":["dummy-ngs"]}}'
```

O retorno inclui o token do worker. Guarde esse valor na workstation.

## Exemplo de `docker run` usado pelo worker

```bash
docker run --rm \
  -v /tmp/ngs-worker/input/job_12:/data/input:ro \
  -v /tmp/ngs-worker/output/job_12:/data/output \
  -v /data/ngs_refs:/data/refs:ro \
  -v /tmp/ngs-worker/run/job_12/job.json:/data/metadata/job.json:ro \
  lab-ngs-dummy:latest \
  python /app/run_pipeline.py \
  --pipeline-name dummy-ngs \
  --metadata /data/metadata/job.json \
  --input-dir /data/input \
  --output-dir /data/output \
  --refs-dir /data/refs
```

## Exemplo de output manifest

```json
{
  "analysis_id": 3,
  "job_id": 12,
  "items": [
    {
      "friendly_name": "summary.tsv",
      "relative_path": "tables/summary.tsv",
      "file_type": "tsv",
      "size": 218,
      "category": "tables",
      "previewable": false,
      "checksum": "sha256..."
    },
    {
      "friendly_name": "coverage.png",
      "relative_path": "plots/coverage.png",
      "file_type": "png",
      "size": 30211,
      "category": "figures",
      "previewable": true,
      "checksum": "sha256..."
    }
  ]
}
```

## Roadmap pós-MVP

- múltiplos workers com capacidade e fila por afinidade
- storage S3 compatível para resultados e uploads
- cancelamento de jobs em execução com sinalização controlada
- auditoria mais detalhada e trilha de eventos
- execução real com FastQC, multiqc ou pipeline de laboratório

Consulte `docs/` para detalhes de arquitetura, deployment e segurança mínima.
