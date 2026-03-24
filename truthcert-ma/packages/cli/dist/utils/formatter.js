"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.formatOutput = void 0;
function toCsvValue(value) {
    if (value === null || value === undefined)
        return '';
    const str = String(value);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}
function flattenForCsv(result) {
    return {
        theta: result?.pooled?.theta,
        se: result?.pooled?.se,
        ci_lower: result?.pooled?.ci?.lower,
        ci_upper: result?.pooled?.ci?.upper,
        p_value: result?.pooled?.p,
        tau2: result?.pooled?.tau2,
        i2: result?.heterogeneity?.I2,
        q: result?.heterogeneity?.Q?.value,
        q_df: result?.heterogeneity?.Q?.df,
        q_p: result?.heterogeneity?.Q?.p,
        k: result?.meta?.k
    };
}
function formatOutput(result, format) {
    const normalized = format.toLowerCase();
    if (normalized === 'json') {
        return JSON.stringify(result, null, 2);
    }
    if (normalized === 'csv') {
        const row = flattenForCsv(result);
        const headers = Object.keys(row);
        const values = headers.map((key) => toCsvValue(row[key]));
        return `${headers.join(',')}\n${values.join(',')}`;
    }
    if (normalized === 'html') {
        const pre = JSON.stringify(result, null, 2)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        return `<!doctype html><html><head><meta charset=\"utf-8\"><title>TruthCert-MA Report</title></head><body><pre>${pre}</pre></body></html>`;
    }
    if (normalized === 'text') {
        const row = flattenForCsv(result);
        return Object.entries(row)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n');
    }
    throw new Error(`Unsupported output format: ${format}`);
}
exports.formatOutput = formatOutput;
//# sourceMappingURL=formatter.js.map