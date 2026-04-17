# Arquitetura

## Decisões

- VPS hospeda frontend, backend, PostgreSQL e storage temporário/final local.
- Workstation nunca recebe conexão de entrada; ela inicia polling e uploads para a VPS.
- Fila de jobs do MVP usa tabela `jobs` no PostgreSQL com polling simples, sem RabbitMQ.
- Storage foi abstraído no backend para facilitar troca futura por S3 compatível.
- Pipeline inicial é `dummy-ngs` em container Docker para validar a orquestração ponta a ponta.

## Componentes

- Frontend React: login, dashboard, criação de análises, upload, detalhes, logs e resultados.
- Backend FastAPI: autenticação JWT, CRUD mínimo de análises, uploads, jobs, arquivos e endpoints do worker.
- Registro de pipelines: backend e worker compartilham uma lista configurável por ambiente, permitindo múltiplas pipelines sem espalhar `docker run` hardcoded.
- PostgreSQL: persistência de usuários, análises, jobs, logs, arquivos e workers.
- Worker Python: polling, claim, download, execução da pipeline, upload de resultados e heartbeat.
- Dummy pipeline container: valida inputs, gera tabela, figuras, relatório HTML e pacote ZIP.

## Armazenamento

- VPS uploads: `storage/uploads/analysis_<id>/`
- VPS resultados: `storage/results/analysis_<id>/job_<id>/`
- VPS metadados: `storage/metadata/analysis_<id>/job_<id>.json`
- Workstation inputs: `INPUT_ROOT/job_<id>/`
- Workstation execução: `RUN_ROOT/job_<id>/`
- Workstation outputs: `OUTPUT_ROOT/job_<id>/`
- Workstation logs: `LOG_ROOT/job_<id>/`

## Status do job

- `pending`
- `downloading`
- `running`
- `uploading_results`
- `completed`
- `failed`
- `cancelled`
