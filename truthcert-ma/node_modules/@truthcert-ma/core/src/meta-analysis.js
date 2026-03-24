"use strict";
/**
 * Main MetaAnalysis class
 * @module meta-analysis
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MetaAnalysis = void 0;
const effect_size_1 = require("./effect-size");
const pooling_1 = require("./pooling");
const heterogeneity_1 = require("./heterogeneity");
const bias_1 = require("./bias");
const clinical_1 = require("./clinical");
const grade_1 = require("./grade");
const sensitivity_1 = require("./sensitivity");
function nntFromRiskDifference(rd, rdCI) {
    // rd = risk_treatment - risk_control, so ARR is negative RD for beneficial effects.
    const arr = -rd;
    const nnt = arr !== 0 ? Math.abs(1 / arr) : Infinity;
    let ci = { lower: NaN, upper: NaN, level: rdCI?.level || 0.95 };
    if (rdCI) {
        const arrLower = -rdCI.upper;
        const arrUpper = -rdCI.lower;
        if (arrLower <= 0 && arrUpper >= 0) {
            ci = { lower: Infinity, upper: Infinity, level: rdCI.level };
        }
        else if (arrLower > 0 && arrUpper > 0) {
            ci = { lower: 1 / arrUpper, upper: 1 / arrLower, level: rdCI.level };
        }
        else {
            ci = {
                lower: Math.abs(1 / arrLower),
                upper: Math.abs(1 / arrUpper),
                level: rdCI.level
            };
        }
    }
    let interpretation;
    if (arr > 0) {
        interpretation = `Treat ${Math.round(nnt)} patients to prevent 1 event`;
    }
    else if (arr < 0) {
        interpretation = `Treat ${Math.round(nnt)} patients to cause 1 additional event (NNH)`;
    }
    else {
        interpretation = 'No effect detected';
    }
    return {
        nnt: Math.round(nnt),
        ci: {
            lower: Math.round(ci.lower),
            upper: Math.round(ci.upper),
            level: ci.level
        },
        arr,
        interpretation
    };
}
/**
 * MetaAnalysis class for running complete meta-analyses
 *
 * @example
 * ```ts
 * const ma = new MetaAnalysis(effects, { method: 'REML' });
 * const results = ma.run();
 *
 * // Or with chaining
 * const results = ma
 *   .calculateEffects()
 *   .pool()
 *   .heterogeneity()
 *   .publicationBias()
 *   .run();
 * ```
 */
class MetaAnalysis {
    /**
     * Create a new MetaAnalysis instance
     *
     * @param data - Effect sizes or raw study data
     * @param options - Analysis options
     */
    constructor(data, options = {}) {
        this.effects = [];
        this._result = {};
        this._steps = [];
        this.options = {
            method: options.method || 'REML',
            model: options.model || 'random',
            confidenceLevel: options.confidenceLevel || 0.95
        };
        this.effectMeasure = options.effectMeasure;
        if (data && data.length > 0) {
            // Check if data is already effect sizes or needs conversion
            if ('yi' in data[0] && 'vi' in data[0]) {
                this.effects = data;
            }
            else if (data && this.effectMeasure) {
                this.effects = (0, effect_size_1.calculateEffectSizes)(data, this.effectMeasure);
            }
        }
    }
    /**
     * Set effect sizes directly
     */
    setEffects(effects) {
        this.effects = effects;
        return this;
    }
    /**
     * Calculate effect sizes from raw data
     */
    calculateEffects(data, measure) {
        const effectMeasure = measure || this.effectMeasure;
        if (!effectMeasure) {
            throw new Error('Effect measure must be specified');
        }
        const rawData = data || this.effects;
        this.effects = (0, effect_size_1.calculateEffectSizes)(rawData, effectMeasure);
        this.effectMeasure = effectMeasure;
        this._steps.push('calculateEffects');
        return this;
    }
    /**
     * Pool effect sizes
     */
    pool() {
        if (this.effects.length === 0) {
            throw new Error('No effects to pool. Call calculateEffects() first or provide effect sizes.');
        }
        const pooled = this.options.model === 'fixed'
            ? (0, pooling_1.fixedEffects)(this.effects, this.options)
            : (0, pooling_1.randomEffects)(this.effects, this.options);
        this._result.pooled = pooled;
        this._result.studies = this.effects;
        if ('tau2' in pooled) {
            this._result.meta = {
                method: this.options.method || 'REML',
                model: this.options.model || 'random',
                effectMeasure: this.effectMeasure,
                k: this.effects.length,
                timestamp: new Date().toISOString()
            };
        }
        this._steps.push('pool');
        return this;
    }
    /**
     * Calculate heterogeneity statistics
     */
    heterogeneity() {
        if (!this._result.pooled) {
            this.pool();
        }
        const tau2 = this._result.pooled.tau2 || 0;
        this._result.heterogeneity = (0, heterogeneity_1.analyzeHeterogeneity)(this.effects, tau2, this._result.pooled.theta, this._result.pooled.se);
        this._steps.push('heterogeneity');
        return this;
    }
    /**
     * Analyze publication bias
     */
    publicationBias() {
        if (!this._result.pooled) {
            this.pool();
        }
        this._result.bias = (0, bias_1.analyzeBias)(this.effects, this._result.pooled);
        this._steps.push('publicationBias');
        return this;
    }
    /**
     * Calculate clinical translation (NNT, etc.)
     */
    clinical(options) {
        if (!this._result.pooled) {
            this.pool();
        }
        const { baselineRisk } = options;
        const theta = this._result.pooled.theta;
        const ci = this._result.pooled.ci;
        switch (this.effectMeasure) {
            case 'OR':
            case 'logOR':
                this._result.clinical = (0, clinical_1.nntFromLogOR)(theta, baselineRisk, ci);
                break;
            case 'RR':
            case 'logRR': {
                const rr = Math.exp(theta);
                const rrCI = {
                    lower: Math.exp(ci.lower),
                    upper: Math.exp(ci.upper),
                    level: ci.level
                };
                this._result.clinical = (0, clinical_1.calculateNNT)(rr, baselineRisk, rrCI);
                break;
            }
            case 'RD':
                this._result.clinical = nntFromRiskDifference(theta, ci);
                break;
            default:
                throw new Error(`Clinical translation supports OR/logOR, RR/logRR, or RD effects; received ${this.effectMeasure ?? 'unknown'}`);
        }
        this._steps.push('clinical');
        return this;
    }
    /**
     * Perform GRADE assessment
     */
    grade(options = {}) {
        if (!this._result.pooled)
            this.pool();
        if (!this._result.heterogeneity)
            this.heterogeneity();
        this._result.grade = (0, grade_1.assessGRADE)(this._result.pooled, this._result.heterogeneity, this._result.bias, { k: this.effects.length, ...options });
        this._steps.push('grade');
        return this;
    }
    /**
     * Perform sensitivity analysis
     */
    sensitivity() {
        if (!this._result.pooled) {
            this.pool();
        }
        this._result.sensitivity = {
            leaveOneOut: (0, sensitivity_1.leaveOneOut)(this.effects, this.options),
            influence: (0, sensitivity_1.influence)(this.effects, this.options)
        };
        this._steps.push('sensitivity');
        return this;
    }
    /**
     * Run all analyses and return complete result
     */
    run() {
        // Run any steps that haven't been run
        if (!this._steps.includes('pool'))
            this.pool();
        if (!this._steps.includes('heterogeneity'))
            this.heterogeneity();
        // Ensure meta is set
        if (!this._result.meta) {
            this._result.meta = {
                method: this.options.method || 'REML',
                model: this.options.model || 'random',
                effectMeasure: this.effectMeasure,
                k: this.effects.length,
                timestamp: new Date().toISOString()
            };
        }
        return this._result;
    }
    /**
     * Run complete analysis with all optional analyses
     */
    runFull(clinicalOptions) {
        this.pool()
            .heterogeneity()
            .publicationBias()
            .sensitivity()
            .grade();
        if (clinicalOptions) {
            this.clinical(clinicalOptions);
        }
        return this.run();
    }
    /**
     * Get forest plot data
     */
    getForestPlotData() {
        if (!this._result.pooled) {
            this.pool();
        }
        const weights = this._result.pooled.weights;
        const z = 1.96; // 95% CI
        return {
            studies: this.effects.map((e, i) => ({
                id: e.study || e.id || `Study ${i + 1}`,
                yi: e.yi,
                ci: {
                    lower: e.yi - z * e.se,
                    upper: e.yi + z * e.se
                },
                weight: weights[i] * 100
            })),
            pooled: {
                yi: this._result.pooled.theta,
                ci: {
                    lower: this._result.pooled.ci.lower,
                    upper: this._result.pooled.ci.upper
                }
            }
        };
    }
    /**
     * Get current results without running additional analyses
     */
    getResults() {
        return { ...this._result };
    }
}
exports.MetaAnalysis = MetaAnalysis;
exports.default = MetaAnalysis;
//# sourceMappingURL=meta-analysis.js.map