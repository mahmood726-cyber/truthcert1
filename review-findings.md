# Review Findings: TruthCert-PairwisePro (Truthcert1)

**Date:** 2026-03-24
**App:** TruthCert-PairwisePro v1.0 (app.js + HTML variants)
**Location:** `C:\HTML apps\Truthcert1\`
**Papers:** PLOS ONE (3 drafts: Draft, Revised, R2), F1000 Software Tool Article

**Note:** This is the base/original Truthcert1 directory. The production work build is at `C:\HTML apps\Truthcert1_work\` (v1.1 code freeze with WebR audit, 101/101 Selenium tests). This review covers the Truthcert1 directory specifically.

---

## Test Results Summary

### Available Test Infrastructure

| Test File | Type | Notes |
|-----------|------|-------|
| selenium_test.py | Selenium browser test | Main test runner |
| test_truthcert_comprehensive.py | Comprehensive test | Extended validation |
| test_truthcert_v2.py | V2 test suite | Updated tests |
| app_test.js | Node/JS unit test | JS-side tests |
| unit_tests.js | Unit tests | Core function tests |
| test_hta.py | HTA validation | Health Technology Assessment |

### Validation Benchmarks (validation_benchmarks.json)

Large benchmark file present with extensive R metafor cross-validation data.

### S4 Validation (S4_Validation_Results.json, 2026-02-24)

- 17/17 PASS (100%)
- BCG dataset validated: tau2 DL/REML/ML, pooled theta, SE, HKSJ CI, PI, Egger
- Proportion and continuous SMD demos validated
- Three-level model and GOSH analysis available

### S3 R Validation (S3_Validation_Results_Complete.txt, 2026-01-20)

- 92 tests total: 24 passed (26.1%), 68 failed
- Study-level yi/vi discrepancies (up to 534% relative error on vi)
- Pooled estimates: ~4-7% relative error
- Tau2 estimators: DL 15.7%, REML 7.3%, ML 3.3% error
- Bias tests (Egger, Begg, Trim-fill): large discrepancies
- LOO analysis: 2-22% relative error

**IMPORTANT**: This S3 run predates the extensive Feb 2026 remediation. The Truthcert1_work build (v1.1) has 101/101 Selenium tests and a full WebR audit suite. However, this Truthcert1 base directory may not have received all fixes.

### Editorial Review (EDITORIAL_REVIEW.md)

- Overall Score: 9.5/10
- Recommendation: ACCEPT
- 413 functions (403 unique), 16,628 lines
- All core methods present: FE, DL, REML, ML, PM, HS, SJ, HE, EB, HKSJ
- Publication bias: Egger, Peters, Trim-fill, PET-PEESE, Copas
- Advanced: Bayesian, Three-level, Dose-response, Bivariate, ROB 2.0, ROBINS-I, PRISMA 2020
- R metafor parity: MH OR/RR, Peto OR, Cook's Distance all validated

### Metafor Comparison (METAFOR_COMPARISON.md)

- Comprehensive mapping of metafor functions to TruthCert equivalents
- 47+ function mappings documented
- Only gap: `rma.glmm()` (GLMM approach) marked missing
- All effect size calculations, bias tests, and diagnostics matched

### PLOS ONE Submission

- Full submission package in `PLOS_ONE_Submission/` directory
- Cover letter, manuscript, figures (5 TIFF), supplementary materials
- S1 Technical Documentation, S2 Monte Carlo Protocol, S3 R Validation

---

## Review Rounds

### 4-Persona Truth Review (2026-03-01)

| Persona | Verdict |
|---------|---------|
| Evidence Traceability | PASS |
| Artifact Consistency | PASS |
| Limitation Honesty | PASS |
| Language Truthfulness | PASS |
| **Overall** | **PASS** |

### F1000 Validation Summary (2026-03-06)

- Claims bounded to available artifacts and documented assumptions
- Primary validation artifact: `PLOS_ONE_Submission\S3_R_Validation_Output.txt`

---

## P0 Issues (Critical / Blocking)

- **P0-1**: S3 R validation (2026-01-20) shows 68/92 failures (26.1% pass rate) with significant numerical discrepancies. While the production Truthcert1_work build resolved these, **it is unclear whether all fixes were backported to this Truthcert1 base directory**. The S4 validation (17/17 PASS) tests a narrower scope and does not cover the full S3 breadth.

## P1 Issues (High / Should-Fix)

- **P1-1**: No consolidated test results file (test_results.json or equivalent) exists in this directory. Test infrastructure is present but latest aggregated results are not saved.
- **P1-2**: The PLOS ONE submission references S3 validation results, but the local S3 file shows 26.1% pass rate. If the submission package includes different (updated) results, the local S3 file creates a misleading evidence trail.
- **P1-3**: `rma.glmm()` equivalent is marked missing in the metafor comparison. If claimed in papers, this is a discrepancy.
- **P1-4**: Relationship between Truthcert1 (this dir) and Truthcert1_work (production) is undocumented. It is unclear which HTML file in this directory is the canonical production version.

## P2 Issues (Low / Nice-to-Have)

- **P2-1**: Multiple HTML variants in directory (bundle, fast, dist, min, optimized, production) -- no document explains which is current.

---

## Verdict

**REVIEW CONDITIONAL**

The S4 validation (17/17) and editorial review (9.5/10 ACCEPT) are positive signals. The 4-persona truth review passed. However, the S3 R validation showing 68/92 failures creates an unresolved evidence gap for this specific directory. The production build at Truthcert1_work has 101/101 tests and a WebR audit, but the fix chain to this base directory is not confirmed. Recommend either: (a) running fresh S3 validation on the current code in this directory, or (b) formally deprecating this directory in favor of Truthcert1_work and documenting the relationship.
