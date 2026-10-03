# Provisionamento e Operação de Infraestrutura — Atividade 2

Três aplicações web (FastAPI) com perfis computacionais diferentes, mais o ferramental para
fazer deploy em uma VM VirtualBox, gerar carga e coletar indicadores de desempenho e uso de recursos.

| App | Perfil | Porta local | Endpoints |
|---|---|---|---|
| `cpu` | CPU-bound | 8001 | `GET /primes` `GET /sort` `GET /matrix` `GET /hash` |
| `memory` | Memory-bound | 8002 | `GET /alloc` `GET /dataset/aggregate` `PUT/GET /cache/{key}` `GET /cache/stats` `DELETE /cache` |
| `io` | IO-bound | 8003 | `POST /files` `GET /files/random` `GET /files/count-lines` `POST /records` `GET /records/{id}` |

Todas expõem também `GET /health`, `GET /metrics` e a documentação interativa em `/docs`.
O que cada endpoint faz e por que ele pertence ao perfil está em [docs/profiles.md](docs/profiles.md).

## Organização

```
src/poi/
  common/        fábrica da aplicação (/health, /metrics, tempo de processamento) e configuração
  cpu_app/       routers/ (validação HTTP) + services/ (carga de trabalho)
  memory_app/
  io_app/
  run.py         ponto de entrada: python -m poi.run <cpu|memory|io>
tests/           testes dos endpoints
monitor/         coletor de uso de recursos (psutil -> CSV)
loadtest/        scripts k6 e wrapper
vm/              criação, configuração e deploy na VM VirtualBox
experiments/     cenários e execução da bateria de experimentos
results/         saída dos experimentos
```

## Rodando localmente

```bash
uv sync
uv run pytest
uv run python -m poi.run cpu        # ou memory, io
curl localhost:8001/health
```

Variáveis de ambiente: `PORT`, `HOST`, `WORKERS` (padrão: um por CPU; `memory` usa sempre 1 por
manter estado em memória), `DATA_DIR` (arquivos da app `io`), `CACHE_MAX_MB` (teto do cache da app `memory`).

## Teste de carga

```bash
loadtest/install_k6.sh                                     # baixa o k6 para .bin/ (uma vez)
loadtest/run_k6.sh cpu 20 30s /tmp/saida http://localhost:8001
```

A carga segue um modelo aberto: `20` é a taxa de chegada em requisições por segundo, mantida
mesmo que a aplicação não dê conta. Requisições que o k6 não consegue disparar aparecem como
`dropped_iterations`. Use `ENDPOINT=primes` (por exemplo) para exercitar um único endpoint em vez do mix.

## Experimentos

Deploy e configuração da VM: [vm/README.md](vm/README.md).

```bash
experiments/run_experiment.sh cpu            # todos os cenários de experiments/scenarios.env, na VM
experiments/run_experiment.sh cpu --local    # ensaio contra a app rodando nesta máquina
```

Para cada cenário de provisionamento a VM é reconfigurada e cada nível de demanda é executado
com o coletor de métricas rodando dentro da VM. Formato da saída: [results/README.md](results/README.md).
