// Variáveis de ambiente:
//   RATE      requisições por segundo (demanda)
//   DURATION  duração do nível (ex.: 60s)
//   BASE_URL  endereço da aplicação
//   ENDPOINT  nome de um endpoint do script, ou "mix" (padrão) para sortear entre todos
//   SUMMARY   caminho do JSON de resumo
export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const RATE = parseInt(__ENV.RATE || '10');
const DURATION = __ENV.DURATION || '30s';
const MAX_VUS = parseInt(__ENV.MAX_VUS || '1000');

export function buildOptions() {
  return {
    scenarios: {
      load: {
        executor: 'constant-arrival-rate',
        rate: RATE,
        timeUnit: '1s',
        duration: DURATION,
        preAllocatedVUs: Math.min(MAX_VUS, Math.max(20, RATE * 2)),
        maxVUs: MAX_VUS,
        gracefulStop: '30s',
      },
    },
    discardResponseBodies: true,
    summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
  };
}

export function params(name) {
  return { tags: { name }, timeout: '30s' };
}

export function pick(endpoints) {
  const names = Object.keys(endpoints);
  const chosen = __ENV.ENDPOINT && __ENV.ENDPOINT !== 'mix' ? __ENV.ENDPOINT : names[Math.floor(Math.random() * names.length)];
  if (!endpoints[chosen]) throw new Error(`ENDPOINT desconhecido: ${chosen} (opções: ${names.join(', ')})`);
  return endpoints[chosen];
}

export function summarize(data, app) {
  const m = data.metrics;
  const value = (metric, key, fallback = 0) => (m[metric] ? m[metric].values[key] : fallback);
  const dur = m.http_req_duration ? m.http_req_duration.values : {};
  const summary = {
    app,
    endpoint: __ENV.ENDPOINT || 'mix',
    rate_target: RATE,
    duration: DURATION,
    requests: value('http_reqs', 'count'),
    throughput_rps: value('http_reqs', 'rate'),
    error_rate: value('http_req_failed', 'rate'),
    dropped_iterations: value('dropped_iterations', 'count'),
    vus_max: value('vus_max', 'max'),
    latency_ms: {
      avg: dur.avg, min: dur.min, p50: dur.med, p90: dur['p(90)'], p95: dur['p(95)'], p99: dur['p(99)'], max: dur.max,
    },
  };
  const line =
    `${app} rate=${RATE}/s -> ${summary.throughput_rps.toFixed(1)} req/s | ` +
    `avg=${(dur.avg || 0).toFixed(1)}ms p95=${(dur['p(95)'] || 0).toFixed(1)}ms p99=${(dur['p(99)'] || 0).toFixed(1)}ms | ` +
    `erros=${(summary.error_rate * 100).toFixed(2)}% descartadas=${summary.dropped_iterations}\n`;
  return {
    [__ENV.SUMMARY || 'k6_summary.json']: JSON.stringify(summary, null, 2),
    stdout: line,
  };
}
