"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadData = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const sync_1 = require("csv-parse/sync");
function toNumber(value) {
    if (typeof value === 'number')
        return value;
    if (typeof value !== 'string')
        return value;
    const trimmed = value.trim();
    if (trimmed === '')
        return value;
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) ? parsed : value;
}
function withNumericValues(row) {
    const out = {};
    for (const [key, value] of Object.entries(row)) {
        out[key] = toNumber(value);
    }
    return out;
}
function normalizeBinaryRow(row) {
    const out = { ...row };
    const hasTotals = typeof out.events1 === 'number' &&
        typeof out.total1 === 'number' &&
        typeof out.events2 === 'number' &&
        typeof out.total2 === 'number';
    if (hasTotals) {
        const events1 = out.events1;
        const total1 = out.total1;
        const events2 = out.events2;
        const total2 = out.total2;
        out.ai = events1;
        out.bi = total1 - events1;
        out.ci = events2;
        out.di = total2 - events2;
    }
    return out;
}
function normalizeContinuousRow(row) {
    const out = { ...row };
    const hasClassicFields = typeof out.mean1 === 'number' &&
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
function normalizeEffectSizeRow(row) {
    const out = { ...row };
    if (typeof out.yi === 'number' && typeof out.vi === 'number' && typeof out.se !== 'number') {
        out.se = Math.sqrt(out.vi);
    }
    return out;
}
function normalizeRow(row) {
    return normalizeEffectSizeRow(normalizeContinuousRow(normalizeBinaryRow(withNumericValues(row))));
}
function parseJson(content) {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed))
        return parsed;
    if (parsed && typeof parsed === 'object') {
        const obj = parsed;
        if (Array.isArray(obj.data))
            return obj.data;
    }
    throw new Error('JSON input must be an array or { data: [...] }');
}
function parseDelimited(content, delimiter) {
    return (0, sync_1.parse)(content, {
        columns: true,
        skip_empty_lines: true,
        trim: true,
        delimiter
    });
}
async function loadData(filePath) {
    if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
    }
    const ext = path.extname(filePath).toLowerCase();
    const content = fs.readFileSync(filePath, 'utf-8');
    let rows;
    if (ext === '.json') {
        rows = parseJson(content);
    }
    else if (ext === '.tsv') {
        rows = parseDelimited(content, '\t');
    }
    else if (ext === '.csv' || ext === '.txt') {
        rows = parseDelimited(content, ',');
    }
    else {
        throw new Error(`Unsupported file extension: ${ext || '(none)'}`);
    }
    return rows
        .filter((row) => Boolean(row) && typeof row === 'object' && !Array.isArray(row))
        .map(normalizeRow);
}
exports.loadData = loadData;
//# sourceMappingURL=data-loader.js.map