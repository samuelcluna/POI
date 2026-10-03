# Resultados

Gerado por `experiments/run_experiment.sh`.

```
results/<app>/<vcpus>cpu_<mem>mb/<demanda>rps/
  k6_summary.json   latência (avg, min, p50, p90, p95, p99, max em ms), vazão, taxa de erro
  vm_metrics.csv    uma amostra por segundo do uso de recursos dentro da VM
  meta.json         cenário, demanda alvo e horário de início/fim (epoch)
  k6_raw.csv.gz     todas as amostras do k6 (somente com RAW=1)
results/<app>/summary.csv   uma linha por (cenário, demanda), com tudo agregado
```

## Colunas de `summary.csv`

| Coluna | Significado |
|---|---|
| `cpus`, `mem_mb` | provisionamento do cenário |
| `rate_target` | demanda aplicada (req/s) |
| `throughput_rps` | vazão medida (req/s concluídas) |
| `error_rate` | fração de requisições com erro ou timeout (30 s) |
| `dropped_iterations` | requisições que o gerador não conseguiu disparar por falta de VUs livres |
| `latency_*_ms` | tempo de resposta |
| `cpu_avg_pct`, `cpu_max_pct` | uso de CPU da VM (100% = todas as vCPUs ocupadas) |
| `iowait_avg_pct` | tempo de CPU esperando IO |
| `mem_used_*_mb`, `swap_used_max_mb` | memória em uso (total − disponível) e swap |
| `disk_*_avg_bytes_s` | bytes lidos/escritos em disco por segundo |
| `proc_cpu_avg_pct` | CPU dos processos da aplicação (100% = uma vCPU) |
| `proc_rss_max_mb` | memória residente dos processos da aplicação |

`vm_metrics.csv` traz as mesmas grandezas por segundo, além do uso de cada vCPU (`cpuN_pct`).
Para regenerar o `summary.csv`: `python3 experiments/summarize.py results/<app>`.
