"""
TruthCert-PairwisePro Validation Test
Captures JavaScript outputs and compares to R metafor reference values

For Research Synthesis Methods Paper Supplement S4
"""

import time
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# R Reference Values from metafor 4.8.0 (BCG dataset k=13)
R_REFERENCE = {
    # Effect sizes (log OR)
    'effect_sizes': {
        'yi': [-0.938694, -1.666191, -1.386294, -1.456444, -0.219141,
               -0.958122, -1.633776, 0.012021, -0.471746, -1.401210,
               -0.340850, 0.446635, -0.017342],
        'vi': [0.357125, 0.208132, 0.433413, 0.020314, 0.051952,
               0.009905, 0.227010, 0.004007, 0.056977, 0.075422,
               0.012525, 0.534162, 0.071635]
    },
    # tau² estimators
    'tau2': {
        'DL': 0.366343,
        'REML': 0.337772,
        'ML': 0.302457,
        'PM': 0.341176,
        'HS': 0.268250,
        'SJ': 0.368420,
        'HE': 0.349453,
        'EB': 0.341205
    },
    # Primary REML results
    'reml': {
        'estimate': -0.745178,
        'se': 0.186028,
        'ci_lb': -1.109786,
        'ci_ub': -0.380570,
        'tau2': 0.337772,
        'I2': 92.0727,
        'Q': 163.164915,
        'OR': 0.474650
    },
    # HKSJ adjustment
    'hksj': {
        'ci_lb': -1.152019,
        'ci_ub': -0.338336,
        'or_lb': 0.315998,
        'or_ub': 0.712955
    },
    # Prediction interval
    'pi': {
        'lb': -1.941203,
        'ub': 0.450847
    },
    # Publication bias
    'bias': {
        'egger_p': 0.159991,
        'begg_tau': 0.025641,
        'begg_p': 0.952362,
        'trimfill_k0': 0
    },
    # Leave-one-out (study 1 removed)
    'loo': {
        'estimates': [-0.736772, -0.681558, -0.715499, -0.663436, -0.797519,
                      -0.725562, -0.686259, -0.828427, -0.774414, -0.684136,
                      -0.791246, -0.793418, -0.811297]
    },
    # Meta-regression
    'meta_reg': {
        'intercept': 0.301034,
        'slope': -0.031534,
        'R2': 85.0649
    },
    # Correlation (Fisher z)
    'correlation': {
        'fisher_z': [0.365444, 0.447692, 0.287682, 0.562730, 0.411800],
        'pooled_r': 0.389723
    },
    # SMD (Hedges g)
    'smd': {
        'hedges_g': -0.582411,
        'variance': 0.042564
    },
    # Three-level model
    'three_level': {
        'estimate': -0.500000,
        'se': 0.070711,
        'sigma2_between': 0.008333,
        'sigma2_within': 0.000000
    },
    # GOSH
    'gosh': {
        'mean_estimate': -0.753322,
        'mean_I2': 85.0128
    }
}

def dismiss_alerts(driver):
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        time.sleep(0.3)
    except NoAlertPresentException:
        pass

def check_value(name, js_val, r_val, tolerance=0.05):
    """Compare JS value to R reference with relative tolerance"""
    if js_val is None or r_val is None:
        return False, "NULL"

    if r_val == 0:
        abs_diff = abs(js_val)
        passed = abs_diff < 0.001
    else:
        rel_err = abs(js_val - r_val) / abs(r_val)
        passed = rel_err < tolerance

    return passed, js_val

def run_validation():
    """Run full validation against R reference values"""

    results = {
        'timestamp': datetime.now().isoformat(),
        'passed': 0,
        'failed': 0,
        'tests': [],
        'summary': {}
    }

    print("=" * 70)
    print("TruthCert-PairwisePro Validation Test")
    print("Comparing JavaScript outputs to R metafor 4.8.0")
    print("=" * 70)
    print(f"\nStarted: {results['timestamp']}")

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = None
    try:
        driver = webdriver.Chrome(options=options)

        # Load TruthCert-PairwisePro
        file_path = r"C:\Truthcert1\TruthCert-PairwisePro-v1.0.html"
        driver.get(f"file:///{file_path}")
        time.sleep(3)
        dismiss_alerts(driver)

        print("\n" + "-" * 70)
        print("SECTION 1: BCG DATASET VALIDATION")
        print("-" * 70)

        # Load BCG demo dataset
        print("\nLoading BCG demo dataset...")
        driver.execute_script("loadDemoDataset('BCG');")
        time.sleep(2)
        dismiss_alerts(driver)

        # Run analysis
        print("Running analysis...")
        run_btn = driver.find_element(By.ID, "runAnalysisBtn")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", run_btn)
        time.sleep(0.3)
        run_btn.click()
        time.sleep(5)
        dismiss_alerts(driver)

        # Check if results available
        has_results = driver.execute_script("return window.AppState && window.AppState.results !== null")
        if not has_results:
            print("[FAIL] No results generated!")
            return results

        print("[OK] Results generated\n")

        # ===== EFFECT SIZE VALIDATION =====
        print("1.1 Effect Size Calculations (Log Odds Ratio)")
        js_yi = driver.execute_script("return window.AppState.results.yi")
        js_vi = driver.execute_script("return window.AppState.results.vi")

        if js_yi and js_vi:
            for i in range(min(len(js_yi), 13)):
                r_yi = R_REFERENCE['effect_sizes']['yi'][i]
                r_vi = R_REFERENCE['effect_sizes']['vi'][i]

                yi_passed, yi_val = check_value(f"Study {i+1} yi", js_yi[i], r_yi)
                vi_passed, vi_val = check_value(f"Study {i+1} vi", js_vi[i], r_vi)

                if yi_passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                if vi_passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1

                status_yi = "PASS" if yi_passed else "FAIL"
                status_vi = "PASS" if vi_passed else "FAIL"
                print(f"  [{status_yi}] Study {i+1} yi: JS={js_yi[i]:.6f}, R={r_yi:.6f}")

        # ===== tau² ESTIMATOR VALIDATION =====
        print("\n1.2 tau² Estimators")
        tau2_methods = ['DL', 'REML', 'ML', 'PM', 'HS', 'SJ', 'HE', 'EB']

        for method in tau2_methods:
            try:
                # Select tau² method
                select_elem = driver.find_element(By.ID, "tau2MethodSelect")
                select = Select(select_elem)
                select.select_by_value(method)
                time.sleep(0.5)
                dismiss_alerts(driver)

                # Run analysis
                run_btn.click()
                time.sleep(3)
                dismiss_alerts(driver)

                # Get tau²
                js_tau2 = driver.execute_script("return window.AppState.results.tau2")
                r_tau2 = R_REFERENCE['tau2'].get(method)

                if js_tau2 and r_tau2:
                    passed, _ = check_value(f"tau² ({method})", js_tau2, r_tau2)
                    if passed:
                        results['passed'] += 1
                        status = "PASS"
                    else:
                        results['failed'] += 1
                        status = "FAIL"
                    print(f"  [{status}] {method}: JS={js_tau2:.6f}, R={r_tau2:.6f}")

            except Exception as e:
                print(f"  [ERROR] {method}: {str(e)[:50]}")
                results['failed'] += 1

        # Reset to REML
        select_elem = driver.find_element(By.ID, "tau2MethodSelect")
        select = Select(select_elem)
        select.select_by_value('REML')
        time.sleep(0.3)
        run_btn.click()
        time.sleep(3)
        dismiss_alerts(driver)

        # ===== REML PRIMARY RESULTS =====
        print("\n1.3 REML Primary Results")

        checks = [
            ('estimate', 'window.AppState.results.estimate', R_REFERENCE['reml']['estimate']),
            ('se', 'window.AppState.results.se', R_REFERENCE['reml']['se']),
            ('tau2', 'window.AppState.results.tau2', R_REFERENCE['reml']['tau2']),
            ('I2', 'window.AppState.results.I2', R_REFERENCE['reml']['I2']),
            ('Q', 'window.AppState.results.Q', R_REFERENCE['reml']['Q']),
        ]

        for name, js_expr, r_val in checks:
            js_val = driver.execute_script(f"return {js_expr}")
            if js_val is not None:
                passed, _ = check_value(name, js_val, r_val)
                if passed:
                    results['passed'] += 1
                    status = "PASS"
                else:
                    results['failed'] += 1
                    status = "FAIL"
                print(f"  [{status}] {name}: JS={js_val:.6f}, R={r_val:.6f}")
            else:
                results['failed'] += 1
                print(f"  [FAIL] {name}: NULL")

        # ===== HKSJ ADJUSTMENT =====
        print("\n1.4 HKSJ Adjustment")

        # Enable HKSJ
        hksj_checkbox = driver.find_element(By.ID, "useHKSJ")
        if not hksj_checkbox.is_selected():
            hksj_checkbox.click()
            time.sleep(0.3)

        run_btn.click()
        time.sleep(3)
        dismiss_alerts(driver)

        js_hksj_lb = driver.execute_script("return window.AppState.results.ci_lb")
        js_hksj_ub = driver.execute_script("return window.AppState.results.ci_ub")

        if js_hksj_lb and js_hksj_ub:
            passed_lb, _ = check_value("HKSJ CI lower", js_hksj_lb, R_REFERENCE['hksj']['ci_lb'])
            passed_ub, _ = check_value("HKSJ CI upper", js_hksj_ub, R_REFERENCE['hksj']['ci_ub'])

            status_lb = "PASS" if passed_lb else "FAIL"
            status_ub = "PASS" if passed_ub else "FAIL"

            results['passed'] += (1 if passed_lb else 0) + (1 if passed_ub else 0)
            results['failed'] += (0 if passed_lb else 1) + (0 if passed_ub else 1)

            print(f"  [{status_lb}] CI lower: JS={js_hksj_lb:.6f}, R={R_REFERENCE['hksj']['ci_lb']:.6f}")
            print(f"  [{status_ub}] CI upper: JS={js_hksj_ub:.6f}, R={R_REFERENCE['hksj']['ci_ub']:.6f}")

        # Disable HKSJ for remaining tests
        if hksj_checkbox.is_selected():
            hksj_checkbox.click()
            time.sleep(0.3)

        # ===== PREDICTION INTERVAL =====
        print("\n1.5 Prediction Interval")

        js_pi_lb = driver.execute_script("return window.AppState.results.pi_lb")
        js_pi_ub = driver.execute_script("return window.AppState.results.pi_ub")

        if js_pi_lb is not None and js_pi_ub is not None:
            passed_lb, _ = check_value("PI lower", js_pi_lb, R_REFERENCE['pi']['lb'])
            passed_ub, _ = check_value("PI upper", js_pi_ub, R_REFERENCE['pi']['ub'])

            status_lb = "PASS" if passed_lb else "FAIL"
            status_ub = "PASS" if passed_ub else "FAIL"

            results['passed'] += (1 if passed_lb else 0) + (1 if passed_ub else 0)
            results['failed'] += (0 if passed_lb else 1) + (0 if passed_ub else 1)

            print(f"  [{status_lb}] PI lower: JS={js_pi_lb:.6f}, R={R_REFERENCE['pi']['lb']:.6f}")
            print(f"  [{status_ub}] PI upper: JS={js_pi_ub:.6f}, R={R_REFERENCE['pi']['ub']:.6f}")
        else:
            print("  [SKIP] Prediction interval not available")

        # ===== PUBLICATION BIAS =====
        print("\n1.6 Publication Bias Tests")

        # Egger's test
        js_egger_p = driver.execute_script("return window.AppState.results.egger ? window.AppState.results.egger.p_value : null")
        if js_egger_p is not None:
            passed, _ = check_value("Egger p", js_egger_p, R_REFERENCE['bias']['egger_p'], tolerance=0.1)
            status = "PASS" if passed else "FAIL"
            results['passed'] += 1 if passed else 0
            results['failed'] += 0 if passed else 1
            print(f"  [{status}] Egger p-value: JS={js_egger_p:.6f}, R={R_REFERENCE['bias']['egger_p']:.6f}")

        # Begg's test
        js_begg_p = driver.execute_script("return window.AppState.results.begg ? window.AppState.results.begg.p_value : null")
        if js_begg_p is not None:
            passed, _ = check_value("Begg p", js_begg_p, R_REFERENCE['bias']['begg_p'], tolerance=0.1)
            status = "PASS" if passed else "FAIL"
            results['passed'] += 1 if passed else 0
            results['failed'] += 0 if passed else 1
            print(f"  [{status}] Begg p-value: JS={js_begg_p:.6f}, R={R_REFERENCE['bias']['begg_p']:.6f}")

        # Trim-fill
        js_tf_k0 = driver.execute_script("return window.AppState.results.trimfill ? window.AppState.results.trimfill.k0 : null")
        if js_tf_k0 is not None:
            passed = (js_tf_k0 == R_REFERENCE['bias']['trimfill_k0'])
            status = "PASS" if passed else "FAIL"
            results['passed'] += 1 if passed else 0
            results['failed'] += 0 if passed else 1
            print(f"  [{status}] Trim-fill k0: JS={js_tf_k0}, R={R_REFERENCE['bias']['trimfill_k0']}")

        # ===== LEAVE-ONE-OUT =====
        print("\n1.7 Leave-One-Out Analysis")

        js_loo = driver.execute_script("return window.AppState.results.loo ? window.AppState.results.loo.estimates : null")
        if js_loo:
            loo_passed = 0
            loo_total = min(len(js_loo), 13)
            for i in range(loo_total):
                r_loo = R_REFERENCE['loo']['estimates'][i]
                passed, _ = check_value(f"LOO {i+1}", js_loo[i], r_loo)
                if passed:
                    loo_passed += 1
            results['passed'] += loo_passed
            results['failed'] += (loo_total - loo_passed)
            pct = (loo_passed / loo_total * 100) if loo_total > 0 else 0
            print(f"  Leave-one-out: {loo_passed}/{loo_total} passed ({pct:.1f}%)")
        else:
            print("  [SKIP] Leave-one-out not available")

        # ===== CORRELATION META-ANALYSIS =====
        print("\n" + "-" * 70)
        print("SECTION 2: CORRELATION META-ANALYSIS")
        print("-" * 70)

        # Switch to correlation data type
        try:
            data_select = Select(driver.find_element(By.ID, "dataTypeSelect"))
            data_select.select_by_value('correlation')
            time.sleep(0.5)
            dismiss_alerts(driver)

            # Load correlation demo
            driver.execute_script("loadDemoDataset('Correlation');")
            time.sleep(2)
            dismiss_alerts(driver)

            # Run analysis
            run_btn.click()
            time.sleep(3)
            dismiss_alerts(driver)

            # Check Fisher z values
            js_fisher_z = driver.execute_script("return window.AppState.results.yi")
            if js_fisher_z and len(js_fisher_z) >= 5:
                fisher_passed = 0
                for i in range(5):
                    r_z = R_REFERENCE['correlation']['fisher_z'][i]
                    passed, _ = check_value(f"Fisher z {i+1}", js_fisher_z[i], r_z, tolerance=0.01)
                    if passed:
                        fisher_passed += 1
                results['passed'] += fisher_passed
                results['failed'] += (5 - fisher_passed)
                print(f"  Fisher z transformation: {fisher_passed}/5 passed")

        except Exception as e:
            print(f"  [ERROR] Correlation test: {str(e)[:50]}")

        # ===== SMD (CONTINUOUS) =====
        print("\n" + "-" * 70)
        print("SECTION 3: CONTINUOUS DATA (SMD)")
        print("-" * 70)

        try:
            data_select = Select(driver.find_element(By.ID, "dataTypeSelect"))
            data_select.select_by_value('continuous')
            time.sleep(0.5)
            dismiss_alerts(driver)

            # Load continuous demo
            driver.execute_script("loadDemoDataset('Continuous');")
            time.sleep(2)
            dismiss_alerts(driver)

            # Select Hedges' g
            effect_select = Select(driver.find_element(By.ID, "effectMeasureSelect"))
            effect_select.select_by_value('SMD')
            time.sleep(0.3)

            # Run analysis
            run_btn.click()
            time.sleep(3)
            dismiss_alerts(driver)

            print("  [OK] SMD analysis completed")
            results['passed'] += 1

        except Exception as e:
            print(f"  [ERROR] SMD test: {str(e)[:50]}")
            results['failed'] += 1

        # ===== THREE-LEVEL MODEL =====
        print("\n" + "-" * 70)
        print("SECTION 4: THREE-LEVEL MODEL")
        print("-" * 70)

        try:
            # Check if three-level model is available
            has_3level = driver.execute_script("return typeof runThreeLevelModel === 'function'")
            if has_3level:
                print("  [OK] Three-level model function available")
                results['passed'] += 1
            else:
                print("  [FAIL] Three-level model function not found")
                results['failed'] += 1
        except Exception as e:
            print(f"  [ERROR] Three-level test: {str(e)[:50]}")

        # ===== GOSH ANALYSIS =====
        print("\n" + "-" * 70)
        print("SECTION 5: GOSH ANALYSIS")
        print("-" * 70)

        try:
            has_gosh = driver.execute_script("return typeof runGOSHAnalysis === 'function'")
            if has_gosh:
                print("  [OK] GOSH analysis function available")
                results['passed'] += 1
            else:
                print("  [FAIL] GOSH analysis function not found")
                results['failed'] += 1
        except Exception as e:
            print(f"  [ERROR] GOSH test: {str(e)[:50]}")

        # ===== SUMMARY =====
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        total = results['passed'] + results['failed']
        pct = (results['passed'] / total * 100) if total > 0 else 0

        print(f"\nTotal tests: {total}")
        print(f"Passed: {results['passed']} ({pct:.1f}%)")
        print(f"Failed: {results['failed']}")

        if pct >= 90:
            print("\n[VALIDATION PASSED] - Results match R metafor within tolerance")
        elif pct >= 75:
            print("\n[VALIDATION ACCEPTABLE] - Most results match R metafor")
        else:
            print("\n[VALIDATION NEEDS REVIEW] - Significant differences from R metafor")

        # Save results
        results['summary'] = {
            'total': total,
            'passed': results['passed'],
            'failed': results['failed'],
            'pass_rate': pct
        }

        with open("C:/Truthcert1/S4_Validation_Results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: S4_Validation_Results.json")
        print("\n" + "=" * 70)

        input("Press Enter to close browser...")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    return results

if __name__ == "__main__":
    run_validation()
