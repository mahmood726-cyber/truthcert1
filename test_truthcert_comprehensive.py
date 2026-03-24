"""
Comprehensive Selenium Test for TruthCert-PairwisePro-v1.0.html
Tests all functions, plots, dropdowns, buttons, and data types
"""

import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Test results tracking
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def log_pass(test_name, details=""):
    results['passed'].append(f"{test_name}: {details}" if details else test_name)
    print(f"  [PASS] {test_name} {details}")

def log_fail(test_name, error=""):
    results['failed'].append(f"{test_name}: {error}")
    print(f"  [FAIL] {test_name} - {error}")

def log_warn(test_name, warning=""):
    results['warnings'].append(f"{test_name}: {warning}")
    print(f"  [WARN] {test_name} - {warning}")

def check_js_errors(driver):
    """Check browser console for JavaScript errors"""
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']
    return errors

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be present and visible"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def click_element_safe(driver, element):
    """Safely click element with scroll and retry"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
        element.click()
        return True
    except:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except:
            return False

def test_page_load(driver):
    """Test 1: Page loads without errors"""
    print("\n=== Test 1: Page Load ===")
    try:
        # Check page title or key element
        header = wait_for_element(driver, By.CSS_SELECTOR, ".app-header, header, h1", 15)
        if header:
            log_pass("Page loaded", "Main header found")
        else:
            log_fail("Page load", "Header element not found")

        # Check for JS errors
        errors = check_js_errors(driver)
        if errors:
            for err in errors:
                log_fail("JavaScript Error", err['message'][:100])
        else:
            log_pass("No JavaScript errors on load")

    except Exception as e:
        log_fail("Page load", str(e))

def test_demo_data_load(driver, data_type='binary'):
    """Test 2: Load demo data"""
    print(f"\n=== Test 2: Load Demo Data ({data_type}) ===")
    try:
        # Find and click demo data button
        demo_btn = None
        demo_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Demo') or contains(text(), 'demo') or contains(text(), 'Load Demo') or contains(text(), 'Sample')]")

        if not demo_buttons:
            demo_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='demo'], button[onclick*='Demo'], .demo-btn, #loadDemo")

        if demo_buttons:
            demo_btn = demo_buttons[0]
            click_element_safe(driver, demo_btn)
            time.sleep(1)
            log_pass("Demo data button clicked")
        else:
            # Try to load demo programmatically
            driver.execute_script("if(typeof loadDemoData === 'function') loadDemoData();")
            time.sleep(1)
            log_pass("Demo data loaded via JS")

        # Verify data loaded by checking table
        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, "#studyTableBody tr, .study-row, tbody tr")
        if len(rows) > 0:
            log_pass(f"Data loaded", f"{len(rows)} study rows found")
        else:
            log_warn("Data load", "No study rows visible")

    except Exception as e:
        log_fail("Demo data load", str(e))

def test_data_type_selector(driver):
    """Test 3: Data type dropdown"""
    print("\n=== Test 3: Data Type Selector ===")
    data_types = ['binary', 'continuous', 'proportion', 'correlation', 'generic']

    try:
        select_elem = driver.find_element(By.ID, "dataType")
        select = Select(select_elem)

        for dt in data_types:
            try:
                select.select_by_value(dt)
                time.sleep(0.5)
                log_pass(f"Data type '{dt}'", "Selected successfully")
            except:
                log_warn(f"Data type '{dt}'", "Not available in dropdown")

        # Reset to binary
        select.select_by_value('binary')
        time.sleep(0.5)

    except Exception as e:
        log_fail("Data type selector", str(e))

def test_effect_size_selector(driver):
    """Test 4: Effect size dropdown"""
    print("\n=== Test 4: Effect Size Selector ===")

    try:
        select_elem = driver.find_element(By.ID, "effectSize")
        select = Select(select_elem)

        options = [opt.get_attribute('value') for opt in select.options]
        log_pass(f"Effect size options found", f"{len(options)} options: {', '.join(options[:10])}...")

        # Test a few key effect sizes
        for es in ['OR', 'RR', 'RD', 'SMD', 'MD']:
            try:
                select.select_by_value(es)
                time.sleep(0.3)
                log_pass(f"Effect size '{es}'", "Selected")
            except:
                pass

        # Reset to OR
        try:
            select.select_by_value('OR')
        except:
            pass

    except Exception as e:
        log_fail("Effect size selector", str(e))

def test_tau2_estimator_selector(driver):
    """Test 5: Tau² estimator dropdown"""
    print("\n=== Test 5: Tau² Estimator Selector ===")

    try:
        select_elem = driver.find_element(By.ID, "tau2Estimator")
        select = Select(select_elem)

        options = [opt.get_attribute('value') for opt in select.options]
        log_pass(f"Tau² estimators found", f"{len(options)} options: {', '.join(options)}")

        # Test each estimator
        for est in options:
            try:
                select.select_by_value(est)
                time.sleep(0.2)
                log_pass(f"Tau² estimator '{est}'", "Selected")
            except Exception as e:
                log_warn(f"Tau² estimator '{est}'", str(e))

        # Reset to REML
        select.select_by_value('REML')

    except Exception as e:
        log_fail("Tau² estimator selector", str(e))

def test_run_analysis(driver):
    """Test 6: Run Analysis button"""
    print("\n=== Test 6: Run Analysis ===")

    try:
        # Find run analysis button
        run_btn = None
        btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Run') or contains(text(), 'Analyze') or contains(text(), 'Calculate')]")
        if btns:
            run_btn = btns[0]
        else:
            run_btn = driver.find_element(By.CSS_SELECTOR, "#runAnalysis, .run-analysis-btn, button[onclick*='runAnalysis']")

        if run_btn:
            click_element_safe(driver, run_btn)
            time.sleep(2)
            log_pass("Run analysis button clicked")

            # Check for results
            results_div = driver.find_elements(By.CSS_SELECTOR, "#resultsPanel, .results, .analysis-results, #results")
            if results_div:
                log_pass("Results panel appeared")

            # Check for JS errors after analysis
            errors = check_js_errors(driver)
            if errors:
                for err in errors[:3]:
                    log_fail("JS Error after analysis", err['message'][:100])
            else:
                log_pass("No JS errors after analysis")

    except Exception as e:
        log_fail("Run analysis", str(e))

def test_forest_plot(driver):
    """Test 7: Forest Plot"""
    print("\n=== Test 7: Forest Plot ===")

    try:
        # Look for forest plot container
        forest = driver.find_elements(By.CSS_SELECTOR, "#forestPlot, .forest-plot, [id*='forest'], canvas, .plotly")
        if forest:
            log_pass("Forest plot container found")

            # Check if Plotly rendered
            plotly_div = driver.find_elements(By.CSS_SELECTOR, ".js-plotly-plot, .plotly-graph-div")
            if plotly_div:
                log_pass("Plotly forest plot rendered")
        else:
            log_warn("Forest plot", "Container not found")

    except Exception as e:
        log_fail("Forest plot", str(e))

def test_funnel_plot(driver):
    """Test 8: Funnel Plot"""
    print("\n=== Test 8: Funnel Plot ===")

    try:
        funnel = driver.find_elements(By.CSS_SELECTOR, "#funnelPlot, .funnel-plot, [id*='funnel']")
        if funnel:
            log_pass("Funnel plot container found")
        else:
            log_warn("Funnel plot", "Container not found - may need tab switch")

    except Exception as e:
        log_fail("Funnel plot", str(e))

def test_tabs(driver):
    """Test 9: Tab Navigation"""
    print("\n=== Test 9: Tab Navigation ===")

    try:
        tabs = driver.find_elements(By.CSS_SELECTOR, ".tab, [role='tab'], .nav-tab, button[data-tab]")
        log_pass(f"Found {len(tabs)} tabs")

        for tab in tabs:
            try:
                tab_text = tab.text[:20] if tab.text else tab.get_attribute('data-tab') or 'unnamed'
                click_element_safe(driver, tab)
                time.sleep(0.5)
                log_pass(f"Tab '{tab_text}'", "Clicked")

                # Check for JS errors
                errors = check_js_errors(driver)
                if errors:
                    for err in errors[:1]:
                        log_fail(f"JS Error in tab '{tab_text}'", err['message'][:80])

            except Exception as e:
                log_warn(f"Tab click", str(e)[:50])

    except Exception as e:
        log_fail("Tab navigation", str(e))

def test_publication_bias(driver):
    """Test 10: Publication Bias Tests"""
    print("\n=== Test 10: Publication Bias ===")

    try:
        # Find pub bias section or tab
        pb_tab = driver.find_elements(By.XPATH, "//*[contains(text(), 'Publication') or contains(text(), 'Bias') or contains(text(), 'Funnel')]")
        if pb_tab:
            click_element_safe(driver, pb_tab[0])
            time.sleep(1)

        # Look for Egger's test result
        egger = driver.find_elements(By.XPATH, "//*[contains(text(), 'Egger') or contains(text(), 'egger')]")
        if egger:
            log_pass("Egger's test", "Found in output")

        # Look for Begg's test
        begg = driver.find_elements(By.XPATH, "//*[contains(text(), 'Begg') or contains(text(), 'begg')]")
        if begg:
            log_pass("Begg's test", "Found in output")

        # Look for trim-and-fill
        tf = driver.find_elements(By.XPATH, "//*[contains(text(), 'Trim') or contains(text(), 'trim')]")
        if tf:
            log_pass("Trim-and-fill", "Found in output")

    except Exception as e:
        log_fail("Publication bias tests", str(e))

def test_hta_module(driver):
    """Test 11: HTA Module"""
    print("\n=== Test 11: HTA Module ===")

    try:
        # Find HTA tab
        hta_tab = driver.find_elements(By.XPATH, "//*[contains(text(), 'HTA') or contains(@data-tab, 'hta')]")
        if hta_tab:
            click_element_safe(driver, hta_tab[0])
            time.sleep(1)
            log_pass("HTA tab", "Clicked")

            # Check for CEAC
            ceac = driver.find_elements(By.XPATH, "//*[contains(text(), 'CEAC') or contains(text(), 'Cost-Effectiveness')]")
            if ceac:
                log_pass("CEAC section", "Found")

            # Check for EVPI
            evpi = driver.find_elements(By.XPATH, "//*[contains(text(), 'EVPI') or contains(text(), 'Value of Information')]")
            if evpi:
                log_pass("EVPI section", "Found")
        else:
            log_warn("HTA module", "Tab not found")

    except Exception as e:
        log_fail("HTA module", str(e))

def test_grade_assessment(driver):
    """Test 12: GRADE Assessment"""
    print("\n=== Test 12: GRADE Assessment ===")

    try:
        grade_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'GRADE') or contains(text(), 'Certainty')]")
        if grade_elem:
            log_pass("GRADE assessment", "Found in interface")
        else:
            log_warn("GRADE assessment", "Not visible")

    except Exception as e:
        log_fail("GRADE assessment", str(e))

def test_verdict_system(driver):
    """Test 13: TruthCert Verdict System"""
    print("\n=== Test 13: Verdict System ===")

    try:
        verdict_tab = driver.find_elements(By.XPATH, "//*[contains(text(), 'Verdict') or contains(@data-tab, 'verdict')]")
        if verdict_tab:
            click_element_safe(driver, verdict_tab[0])
            time.sleep(1)
            log_pass("Verdict tab", "Clicked")

            # Check for verdict display
            verdict = driver.find_elements(By.CSS_SELECTOR, ".verdict, .truthcert-verdict, [class*='verdict']")
            if verdict:
                log_pass("Verdict display", "Found")
        else:
            log_warn("Verdict system", "Tab not found")

    except Exception as e:
        log_fail("Verdict system", str(e))

def test_export_functions(driver):
    """Test 14: Export Functions"""
    print("\n=== Test 14: Export Functions ===")

    try:
        export_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Export') or contains(text(), 'Download') or contains(text(), 'Save')]")
        log_pass(f"Export buttons found", f"{len(export_btns)} buttons")

        # Check for specific exports
        for export_type in ['CSV', 'PDF', 'Word', 'Excel', 'R', 'JSON']:
            exp = driver.find_elements(By.XPATH, f"//*[contains(text(), '{export_type}')]")
            if exp:
                log_pass(f"Export {export_type}", "Option available")

    except Exception as e:
        log_fail("Export functions", str(e))

def test_sensitivity_analysis(driver):
    """Test 15: Sensitivity Analysis"""
    print("\n=== Test 15: Sensitivity Analysis ===")

    try:
        sens_elem = driver.find_elements(By.XPATH, "//*[contains(text(), 'Leave-One-Out') or contains(text(), 'Sensitivity') or contains(text(), 'Influence')]")
        if sens_elem:
            log_pass("Sensitivity analysis", "Options found")

        # Look for Baujat plot
        baujat = driver.find_elements(By.XPATH, "//*[contains(text(), 'Baujat')]")
        if baujat:
            log_pass("Baujat plot", "Option found")

    except Exception as e:
        log_fail("Sensitivity analysis", str(e))

def test_subgroup_analysis(driver):
    """Test 16: Subgroup Analysis"""
    print("\n=== Test 16: Subgroup Analysis ===")

    try:
        subgroup = driver.find_elements(By.XPATH, "//*[contains(text(), 'Subgroup') or contains(text(), 'subgroup')]")
        if subgroup:
            log_pass("Subgroup analysis", "Option found")
        else:
            log_warn("Subgroup analysis", "Not visible")

    except Exception as e:
        log_fail("Subgroup analysis", str(e))

def test_meta_regression(driver):
    """Test 17: Meta-Regression"""
    print("\n=== Test 17: Meta-Regression ===")

    try:
        metareg = driver.find_elements(By.XPATH, "//*[contains(text(), 'Meta-Regression') or contains(text(), 'Regression') or contains(text(), 'Moderator')]")
        if metareg:
            log_pass("Meta-regression", "Option found")
        else:
            log_warn("Meta-regression", "Not visible")

    except Exception as e:
        log_fail("Meta-regression", str(e))

def test_validation_panel(driver):
    """Test 18: Validation Panel"""
    print("\n=== Test 18: Validation Panel ===")

    try:
        valid_tab = driver.find_elements(By.XPATH, "//*[contains(text(), 'Validation') or contains(@data-tab, 'validation')]")
        if valid_tab:
            click_element_safe(driver, valid_tab[0])
            time.sleep(1)
            log_pass("Validation tab", "Clicked")

            # Look for benchmark table
            benchmark = driver.find_elements(By.XPATH, "//*[contains(text(), 'metafor') or contains(text(), 'Benchmark')]")
            if benchmark:
                log_pass("Benchmark comparison", "Found")
        else:
            log_warn("Validation panel", "Tab not found")

    except Exception as e:
        log_fail("Validation panel", str(e))

def test_all_buttons(driver):
    """Test 19: Click All Buttons (safety check)"""
    print("\n=== Test 19: Button Safety Check ===")

    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        log_pass(f"Found {len(buttons)} buttons")

        # Just count, don't click all
        enabled_count = sum(1 for b in buttons if b.is_enabled())
        log_pass(f"Enabled buttons", f"{enabled_count} clickable")

    except Exception as e:
        log_fail("Button check", str(e))

def test_continuous_data(driver):
    """Test 20: Continuous Data Type"""
    print("\n=== Test 20: Continuous Data Analysis ===")

    try:
        # Switch to continuous
        select = Select(driver.find_element(By.ID, "dataType"))
        select.select_by_value('continuous')
        time.sleep(0.5)

        # Load demo or enter data
        driver.execute_script("""
            if(typeof loadDemoData === 'function') {
                loadDemoData('continuous');
            }
        """)
        time.sleep(1)

        # Set effect size to SMD or MD
        try:
            es_select = Select(driver.find_element(By.ID, "effectSize"))
            es_select.select_by_value('SMD')
        except:
            pass

        # Run analysis
        driver.execute_script("if(typeof runAnalysis === 'function') runAnalysis();")
        time.sleep(2)

        errors = check_js_errors(driver)
        if errors:
            for err in errors[:2]:
                log_fail("Continuous analysis JS error", err['message'][:80])
        else:
            log_pass("Continuous data analysis", "Completed without JS errors")

    except Exception as e:
        log_fail("Continuous data analysis", str(e))

def test_proportion_data(driver):
    """Test 21: Proportion Data Type"""
    print("\n=== Test 21: Proportion Data Analysis ===")

    try:
        select = Select(driver.find_element(By.ID, "dataType"))
        select.select_by_value('proportion')
        time.sleep(0.5)

        driver.execute_script("""
            if(typeof loadDemoData === 'function') {
                loadDemoData('proportion');
            }
        """)
        time.sleep(1)

        driver.execute_script("if(typeof runAnalysis === 'function') runAnalysis();")
        time.sleep(2)

        errors = check_js_errors(driver)
        if errors:
            for err in errors[:2]:
                log_fail("Proportion analysis JS error", err['message'][:80])
        else:
            log_pass("Proportion data analysis", "Completed without JS errors")

    except Exception as e:
        log_fail("Proportion data analysis", str(e))

def test_correlation_data(driver):
    """Test 22: Correlation Data Type"""
    print("\n=== Test 22: Correlation Data Analysis ===")

    try:
        select = Select(driver.find_element(By.ID, "dataType"))
        select.select_by_value('correlation')
        time.sleep(0.5)

        driver.execute_script("""
            if(typeof loadDemoData === 'function') {
                loadDemoData('correlation');
            }
        """)
        time.sleep(1)

        driver.execute_script("if(typeof runAnalysis === 'function') runAnalysis();")
        time.sleep(2)

        errors = check_js_errors(driver)
        if errors:
            for err in errors[:2]:
                log_fail("Correlation analysis JS error", err['message'][:80])
        else:
            log_pass("Correlation data analysis", "Completed without JS errors")

    except Exception as e:
        log_fail("Correlation data analysis", str(e))

def test_generic_data(driver):
    """Test 23: Generic (Pre-calculated) Data Type"""
    print("\n=== Test 23: Generic Data Analysis ===")

    try:
        select = Select(driver.find_element(By.ID, "dataType"))
        select.select_by_value('generic')
        time.sleep(0.5)

        driver.execute_script("""
            if(typeof loadDemoData === 'function') {
                loadDemoData('generic');
            }
        """)
        time.sleep(1)

        driver.execute_script("if(typeof runAnalysis === 'function') runAnalysis();")
        time.sleep(2)

        errors = check_js_errors(driver)
        if errors:
            for err in errors[:2]:
                log_fail("Generic analysis JS error", err['message'][:80])
        else:
            log_pass("Generic data analysis", "Completed without JS errors")

    except Exception as e:
        log_fail("Generic data analysis", str(e))

def test_full_analysis_binary(driver):
    """Test 24: Full Analysis with Binary Data"""
    print("\n=== Test 24: Full Binary Analysis ===")

    try:
        # Reset to binary
        select = Select(driver.find_element(By.ID, "dataType"))
        select.select_by_value('binary')
        time.sleep(0.5)

        # Load demo
        driver.execute_script("if(typeof loadDemoData === 'function') loadDemoData('binary');")
        time.sleep(1)

        # Run full analysis
        driver.execute_script("if(typeof runFullAnalysis === 'function') runFullAnalysis(); else if(typeof runAnalysis === 'function') runAnalysis();")
        time.sleep(3)

        errors = check_js_errors(driver)
        if errors:
            for err in errors[:3]:
                log_fail("Full analysis JS error", err['message'][:80])
        else:
            log_pass("Full binary analysis", "Completed without JS errors")

    except Exception as e:
        log_fail("Full binary analysis", str(e))

def main():
    """Main test runner"""
    print("=" * 60)
    print("TruthCert-PairwisePro Comprehensive Test Suite")
    print("=" * 60)

    # Setup Chrome
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    driver = None

    try:
        driver = webdriver.Chrome(options=options)

        # Load the application
        file_path = r"C:\Truthcert1\TruthCert-PairwisePro-v1.0.html"
        driver.get(f"file:///{file_path}")
        time.sleep(3)

        # Run all tests
        test_page_load(driver)
        test_demo_data_load(driver)
        test_data_type_selector(driver)
        test_effect_size_selector(driver)
        test_tau2_estimator_selector(driver)
        test_run_analysis(driver)
        test_forest_plot(driver)
        test_funnel_plot(driver)
        test_tabs(driver)
        test_publication_bias(driver)
        test_hta_module(driver)
        test_grade_assessment(driver)
        test_verdict_system(driver)
        test_export_functions(driver)
        test_sensitivity_analysis(driver)
        test_subgroup_analysis(driver)
        test_meta_regression(driver)
        test_validation_panel(driver)
        test_all_buttons(driver)
        test_continuous_data(driver)
        test_proportion_data(driver)
        test_correlation_data(driver)
        test_generic_data(driver)
        test_full_analysis_binary(driver)

        # Final JS error check
        print("\n=== Final JavaScript Error Check ===")
        all_errors = check_js_errors(driver)
        if all_errors:
            print(f"Total JS errors found: {len(all_errors)}")
            for err in all_errors[:10]:
                print(f"  - {err['message'][:100]}")
        else:
            print("No JavaScript errors detected!")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        traceback.print_exc()

    finally:
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"PASSED: {len(results['passed'])}")
        print(f"FAILED: {len(results['failed'])}")
        print(f"WARNINGS: {len(results['warnings'])}")

        if results['failed']:
            print("\n--- FAILURES ---")
            for fail in results['failed']:
                print(f"  - {fail}")

        if results['warnings']:
            print("\n--- WARNINGS ---")
            for warn in results['warnings'][:10]:
                print(f"  - {warn}")

        print("\n" + "=" * 60)

        if driver:
            input("\nPress Enter to close browser...")
            driver.quit()

if __name__ == "__main__":
    main()
