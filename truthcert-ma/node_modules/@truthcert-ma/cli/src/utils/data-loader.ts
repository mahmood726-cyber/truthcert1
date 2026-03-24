import * as fs from 'fs';
import * as path from 'path';
import { parse as parseCsv } from 'csv-parse/sync';

type JsonRecord = Record<string, unknown>;

function toNumber(value: unknown): unknown {
  if (typeof value === 'number') return value;
  if (typeof value !== 'string') return value;
  const trimmed = value.trim();
  if (trimmed === '') return value;
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : value;
}

function withNumericValues(row: JsonRecord): JsonRecord {
  const out: JsonRecord = {};
  for (const [key, value] of Object.entries(row)) {
    out[key] = toNumber(value);
  }
  return out;
}

function normalizeBinaryRow(row: JsonRecord): JsonRecord {
  const out = { ...row };
  const hasTotals =
    typeof out.events1 === 'number' &&
    typeof out.total1 === 'number' &&
    typeof out.events2 === 'number' &&
    typeof out.total2 === 'number';

  if (hasTotals) {
    const events1 = out.events1 as number;
    const total1 = out.total1 as number;
    const events2 = out.events2 as number;
    const total2 = out.total2 as number;
    out.ai = events1;
    out.bi = total1 - events1;
    out.ci = events2;
    out.di = total2 - events2;
  }

  return out;
}

function normalizeContinuousRow(row: JsonRecord): JsonRecord {
  const out = { ...row };
  const hasClassicFields =
    typeof out.mean1 === 'number' &&
    typeof out.sd1 === 'number' &&
    typeof out.n1 === 'number' &&
    typeof out.mean2 === 'number' &&
    typeof out.sd2 === 'number' &&
    typeof out.n2 === 'number';

  if (hasClassicFields) {
    out.m1i = out.mean1;
    out.sd1i = out.sd1;
    out.n1i = out.n1;
    out.m2i = out.mean2;
    out.sd2i = out.sd2;
    out.n2i = out.n2;
  }

  return out;
}

function normalizeEffectSizeRow(row: JsonRecord): JsonRecord {
  const out = { ...row };
  if (typeof out.yi === 'number' && typeof out.vi === 'number' && typeof out.se !== 'number') {
    out.se = Math.sqrt(out.vi);
  }
  return out;
}

function normalizeRow(row: JsonRecord): JsonRecord {
  return normalizeEffectSizeRow(normalizeContinuousRow(normalizeBinaryRow(withNumericValues(row))));
}

function parseJson(content: string): unknown[] {
  const parsed = JSON.parse(content) as unknown;
  if (Array.isArray(parsed)) return parsed;
  if (parsed && typeof parsed === 'object') {
    const obj = parsed as Record<string, unknown>;
    if (Array.isArray(obj.data)) return obj.data;
  }
  throw new Error('JSON input must be an array or { data: [...] }');
}

function parseDelimited(content: string, delimiter: string): unknown[] {
  return parseCsv(content, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
    delimiter
  }) as unknown[];
}

export async function loadData(filePath: string): Promise<any[]> {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const ext = path.extname(filePath).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf-8');

  let rows: unknown[];
  if (ext === '.json') {
    rows = parseJson(content);
  } else if (ext === '.tsv') {
    rows = parseDelimited(content, '\t');
  } else if (ext === '.csv' || ext === '.txt') {
    rows = parseDelimited(content, ',');
  } else {
    throw new Error(`Unsupported file extension: ${ext || '(none)'}`);
  }

  return rows
    .filter((row): row is JsonRecord => Boolean(row) && typeof row === 'object' && !Array.isArray(row))
    .map(normalizeRow);
}
