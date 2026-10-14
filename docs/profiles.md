# Perfis das aplicações

## CPU-bound (`cpu`)

Stateless: cada requisição faz um cálculo do zero e não guarda nada.

| Endpoint | Parâmetro (padrão) | Trabalho |
|---|---|---|
| `GET /primes` | `limit` (50000) | conta primos por divisão sucessiva |
| `GET /sort` | `n` (200000) | gera `n` números e ordena |
| `GET /matrix` | `size` (100) | multiplica duas matrizes `size`×`size` em Python puro |
| `GET /hash` | `iterations` (150000) | PBKDF2-SHA256 |

O recurso que limita é ciclo de CPU: a memória por requisição é pequena e não há IO. A aplicação
sobe um processo worker por vCPU, porque um único processo Python só usa um núcleo de cada vez
para código Python (GIL). Com isso, adicionar vCPUs à VM aumenta de fato a capacidade.

## Memory-bound (`memory`)

Stateful: o cache vive na memória do processo, por isso roda com um único worker.

| Endpoint | Parâmetro (padrão) | Trabalho |
|---|---|---|
| `GET /alloc` | `mb` (64), `hold_ms` (250) | aloca, toca todas as páginas, segura pelo tempo pedido e libera |
| `GET /dataset/aggregate` | `rows` (50000) | monta o dataset inteiro em memória e depois agrega |
| `PUT /cache/{key}` | `kb` (256) | grava um valor no cache em memória (LRU com teto `CACHE_MAX_MB`, padrão 256) |
| `GET /cache/{key}` | | lê do cache (404 se a chave não existe) |
| `GET /cache/stats`, `DELETE /cache` | | ocupação do cache / esvazia |

A memória em uso cresce com a concorrência: cada `/alloc` em andamento segura `mb` MB. Quando a
soma passa da RAM da VM, o sistema entra em swap e o tempo de resposta dispara, ou o OOM killer
encerra o processo (o systemd o reinicia e as requisições em andamento falham).

Por rodar em um único worker, com RAM sobrando o limite passa a ser a CPU desse worker
(`/dataset/aggregate` também gasta CPU para montar os registros). O perfil de memória aparece
em cenários com pouca RAM; `ALLOC_MB` no k6 aumenta a pressão por requisição.

## IO-bound (`io`)

| Endpoint | Parâmetro (padrão) | Trabalho |
|---|---|---|
| `POST /files` | `kb` (256) | grava um arquivo e só responde depois do `fsync` |
| `GET /files/random` | | lê do disco um dos arquivos semeados (32 × 1 MB) |
| `GET /files/count-lines` | | conta as linhas de um arquivo de 16 MB, lendo em blocos |
| `POST /records` | `size` (512) | insere no SQLite com commit sincronizado em disco |
| `GET /records/{id}` | | busca um registro |

Pouco CPU por requisição; o tempo é gasto esperando o disco. Antes de cada leitura a aplicação
pede ao kernel para descartar o cache daquele arquivo (`posix_fadvise(DONTNEED)`), para a leitura
ir ao disco em vez de virar cópia de memória. Isso funciona em ext4 (a VM); em ZFS o pedido é
ignorado e as leituras saem do cache.

Tamanhos dos dados semeados: `IO_SEED_FILES`, `IO_SEED_FILE_KB`, `IO_LINES_MB`, `IO_SEED_RECORDS`.

## Medição local de referência

Execuções curtas (10–12 s por nível) em uma máquina de 12 núcleos, só para conferir os perfis.
Não substituem os experimentos na VM.

| App | Demanda | Vazão | p95 | CPU dos processos | RSS máx. |
|---|---|---|---|---|---|
| cpu (2 workers) | 10 req/s | 10,0 | 88 ms | 54% | 146 MB |
| cpu (2 workers) | 40 req/s | 37,4 | 1368 ms | 249% | 238 MB |
| memory | 5 req/s | 5,1 | 333 ms | 15% | 130 MB |
| memory | 40 req/s | 39,2 | 819 ms | 86% | 528 MB |
| io (2 workers) | 10 req/s | 10,0 | 62 ms | 22% | 230 MB |
| io (2 workers) | 120 req/s | 119,9 | 64 ms | 100% | 291 MB |

A app `cpu` satura perto de 35 req/s com 2 workers e a memória fica estável. O uso passa de 200% porque o `/hash` roda em código nativo fora do GIL e ocupa núcleos além de um por worker; na VM o teto é o número de vCPUs. Na app `memory` o
RSS cresce com a demanda. A medição da app `io` foi feita em ZFS, então as leituras vieram do
cache e o disco não chegou a limitar; o comportamento IO-bound foi confirmado na VM (ext4), onde a leitura em disco cresceu com a demanda.
