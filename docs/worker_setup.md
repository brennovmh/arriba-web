# Worker Setup

## Pré-requisitos

- Linux com Docker funcional
- diretório local com referências em `REFS_DIR`
- conectividade de saída para a VPS

## Passos

1. Registrar o worker no backend e obter o token.
2. Configurar `worker/.env`.
3. Construir ou disponibilizar a imagem Docker da pipeline.
4. Rodar o processo `python -m app.main` como serviço `systemd` na workstation.

## Exemplo de unit file

```ini
[Unit]
Description=Lab NGS Worker
After=network-online.target docker.service

[Service]
WorkingDirectory=/opt/lab-ngs/platform/worker
EnvironmentFile=/opt/lab-ngs/platform/worker/.env
ExecStart=/opt/lab-ngs/platform/worker/.venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Trocar pipeline dummy por pipeline real

1. Crie um novo runner ou adapte `DockerPipelineRunner`.
2. Troque `DUMMY_PIPELINE_IMAGE`.
3. Ajuste os parâmetros de entrada e a geração do `manifest`.
4. Garanta que a pipeline escreva outputs dentro de `/data/output`.
