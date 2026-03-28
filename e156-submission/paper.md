Mahmood Ahmad
Tahir Heart Institute
author@example.com

TruthCert-MA: A Cross-Platform JavaScript Meta-Analysis Engine Validated Against R

Can a single JavaScript library provide a complete meta-analysis engine validated for both browser and server-side deployment scenarios? TruthCert-MA is a TypeScript library offering effect-size calculation, random-effects pooling with REML and DerSimonian-Laird estimators, heterogeneity quantification, publication bias diagnostics, and forest plot generation, distributed as CLI, Node package, browser bundle, and REST API. The library uses a plugin architecture for custom estimators and formatters while maintaining a zero-dependency core validated against R metafor for odds ratios, risk ratios, and mean differences. All pooled estimates matched R metafor within 0.001 for point estimates and 0.01 for confidence interval bounds across the full benchmark suite. Cross-platform reproducibility was verified by running identical analyses through CLI, programmatic, and browser entry points yielding bitwise-identical JSON output files. These results support using JavaScript-native statistical engines as credible alternatives to R-based meta-analysis workflows. However, the limitation of single-threaded browser execution means analyses exceeding ten thousand studies may encounter performance degradation without worker parallelization.

Outside Notes

Type: methods
Primary estimand: Pooled effect size (OR/RR/MD/SMD)
App: TruthCert-MA v1.0
Data: R metafor validation benchmarks (OR, RR, MD, SMD)
Code: https://github.com/mahmood726-cyber/truthcert1
Version: 1.0
Validation: DRAFT

References

1. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. BMJ. 1997;315(7109):629-634.
2. Duval S, Tweedie R. Trim and fill: a simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. Biometrics. 2000;56(2):455-463.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI (Claude, Anthropic) was used as a constrained synthesis engine operating on structured inputs and predefined rules for infrastructure generation, not as an autonomous author. The 156-word body was written and verified by the author, who takes full responsibility for the content. This disclosure follows ICMJE recommendations (2023) that AI tools do not meet authorship criteria, COPE guidance on transparency in AI-assisted research, and WAME recommendations requiring disclosure of AI use. All analysis code, data, and versioned evidence capsules (TruthCert) are archived for independent verification.
