import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, buildOptions, params, pick, summarize } from './lib.js';

export const options = buildOptions();

const ALLOC_MB = __ENV.ALLOC_MB || '64';
const CACHE_KEYS = parseInt(__ENV.CACHE_KEYS || '200');
const key = () => `k${Math.floor(Math.random() * CACHE_KEYS)}`;
// 404 = chave ainda não gravada, não conta como erro
const hitOrMiss = http.expectedStatuses(200, 404);

const ENDPOINTS = {
  alloc: () => http.get(`${BASE_URL}/alloc?mb=${ALLOC_MB}`, params('alloc')),
  dataset: () => http.get(`${BASE_URL}/dataset/aggregate`, params('dataset')),
  cache_put: () => http.put(`${BASE_URL}/cache/${key()}`, null, params('cache_put')),
  cache_get: () =>
    http.get(`${BASE_URL}/cache/${key()}`, Object.assign(params('cache_get'), { responseCallback: hitOrMiss })),
};

export default function () {
  check(pick(ENDPOINTS)(), { 'status ok': (r) => r.status === 200 || r.status === 404 });
}

export function handleSummary(data) {
  return summarize(data, 'memory');
}
