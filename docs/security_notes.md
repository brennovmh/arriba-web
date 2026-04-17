# Segurança mínima do MVP

- Workstation não é exposta publicamente.
- Comunicação do worker é sempre iniciada da workstation para a VPS.
- Usuários autenticam com JWT.
- Workers autenticam com token exclusivo por workstation.
- Upload aceita apenas extensões FASTQ configuradas.
- Upload tem limite de tamanho configurável.
- Paths são normalizados para mitigar path traversal.
- Diretórios são segregados por análise e job.
- O backend limita downloads ao dono da análise.

## Pendências naturais do MVP

- renovar tokens de worker
- rate limiting
- auditoria mais completa
- HTTPS obrigatório no ambiente publicado
- rotação e retenção formal de logs
