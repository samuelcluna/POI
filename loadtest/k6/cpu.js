import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, buildOptions, params, pick, summarize } from './lib.js';

export const options = buildOptions();

const ENDPOINTS = {
  primes: () => http.get(`${BASE_URL}/primes`, params('primes')),
  sort: () => http.get(`${BASE_URL}/sort`, params('sort')),
  matrix: () => http.get(`${BASE_URL}/matrix`, params('matrix')),
  hash: () => http.get(`${BASE_URL}/hash`, params('hash')),
};

export default function () {
  check(pick(ENDPOINTS)(), { 'status 200': (r) => r.status === 200 });
}

export function handleSummary(data) {
  return summarize(data, 'cpu');
}
