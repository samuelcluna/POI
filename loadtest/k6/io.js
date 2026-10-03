import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, buildOptions, params, pick, summarize } from './lib.js';

export const options = buildOptions();

const SEEDED_RECORDS = parseInt(__ENV.SEEDED_RECORDS || '1000');
const recordId = () => 1 + Math.floor(Math.random() * SEEDED_RECORDS);

const ENDPOINTS = {
  file_write: () => http.post(`${BASE_URL}/files`, null, params('file_write')),
  file_read: () => http.get(`${BASE_URL}/files/random`, params('file_read')),
  count_lines: () => http.get(`${BASE_URL}/files/count-lines`, params('count_lines')),
  record_write: () => http.post(`${BASE_URL}/records`, null, params('record_write')),
  record_read: () => http.get(`${BASE_URL}/records/${recordId()}`, params('record_read')),
};

export default function () {
  check(pick(ENDPOINTS)(), { 'status 200': (r) => r.status === 200 });
}

export function handleSummary(data) {
  return summarize(data, 'io');
}
