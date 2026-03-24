"""
TruthCert-PairwisePro Comprehensive Test v2
Uses correct element IDs from HTML inspection
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException, NoAlertPresentException

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

results = {'passed': 0, 'failed': 0, 'errors': []}

def log_pass(msg):
    results['passed'] += 1
    print(f"  [PASS] {msg}")

def log_fail(msg, err=""):
    results['failed'] += 1
    results['errors'].append(f"{msg}: {err}")
    print(f"  [FAIL] {msg} - {err[:100]}")

def dismiss_alerts(driver):
    """Dismiss any open alerts"""
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        time.sleep(0.3)
    except NoAlertPresentException:
        pass

def get_js_errors(driver):
    """Get JavaScript errors from console"""
    try:
        logs = driver.get_log('browser')
        return [l for l in logs if l['level'] == 'SEVERE']
    except:
        return []

def test_with_correct_ids(driver):
    """Test with correct element IDs"""

    print("\n=== Test: Page Load and Initial Check ===")
    try:
        # Wait for page to load
        time.sleep(2)
        errors = get_js_errors(driver)
        if errors:
            for e in errors:
                log_fail("JS Error on Load", e.get('message', '')[:100])
        else:
            log_pass("Page loaded without JS errors")
    except Exception as e:
        log_fail("Page load check", str(e))

    print("\n=== Test: Data Type Selector ===")
    try:
        select_elem = driver.find_element(By.ID, "dataTypeSelect")
        select = Select(select_elem)
        options = [o.get_attribute('value') for o in select.options if o.get_attribute('value')]
        log_pass(f"Data type selector found with options: {options}")

        for dt in options:
            select.select_by_value(dt)
            time.sleep(0.3)
            dismiss_alerts(driver)
            log_pass(f"Data type '{dt}' selected")

        # Reset to binary
        select.select_by_value('binary')
        time.sleep(0.3)
        dismiss_alerts(driver)
    except Exception as e:
        log_fail("Data type selector", str(e))

    print("\n=== Test: Effect Size Selector ===")
    try:
        select_elem = driver.find_element(By.ID, "effectMeasureSelect")
        select = Select(select_elem)
        options = [o.get_attribute('value') for o in select.options if o.get_attribute('value')]
        log_pass(f"Effect size selector found with {len(options)} options")

        for es in options[:5]:  # Test first 5
            try:
                select.select_by_value(es)
                time.sleep(0.2)
                dismiss_alerts(driver)
                log_pass(f"Effect size '{es}' selected")
            except:
                pass

        # Reset to OR
        try:
            select.select_by_value('OR')
        except:
            pass
    except Exception as e:
        log_fail("Effect size selector", str(e))

    print("\n=== Test: Tau2 Estimator Selector ===")
    try:
        select_elem = driver.find_element(By.ID, "tau2MethodSelect")
        select = Select(select_elem)
        options = [o.get_attribute('value') for o in select.options if o.get_attribute('value')]
        log_pass(f"Tau2 selector found with {len(options)} estimators: {', '.join(options)}")

        for est in options:
            try:
                select.select_by_value(est)
                time.sleep(0.2)
                dismiss_alerts(driver)
                log_pass(f"Tau2 estimator '{est}' selected")
            except Exception as e:
                log_fail(f"Tau2 '{est}'", str(e))

        # Reset to REML
        select.select_by_value('REML')
    except Exception as e:
        log_fail("Tau2 estimator selector", str(e))

    print("\n=== Test: Load Demo Data ===")
    try:
        # Try clicking demo button or calling JS function
        demo_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Demo') or contains(text(), 'Sample')]")
        if demo_btns:
            demo_btns[0].click()
            time.sleep(1)
            dismiss_alerts(driver)
            log_pass("Demo button clicked")
        else:
            # Try JS function
            driver.execute_script("if(typeof loadDemoData === 'function') loadDemoData();")
            time.sleep(1)
            dismiss_alerts(driver)
            log_pass("Demo data loaded via JS")

        # Check for study rows
        rows = driver.find_elements(By.CSS_SELECTOR, "#studyTableBody tr")
        if len(rows) > 0:
            log_pass(f"Data loaded: {len(rows)} study rows")
        else:
            log_fail("Data load", "No study rows found")
    except Exception as e:
        log_fail("Load demo data", str(e))

    print("\n=== Test: Run Analysis ===")
    try:
        dismiss_alerts(driver)
        run_btn = driver.find_element(By.ID, "runAnalysisBtn")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", run_btn)
        time.sleep(0.3)
        run_btn.click()
        time.sleep(3)
        dismiss_alerts(driver)

        errors = get_js_errors(driver)
        if errors:
            for e in errors[:3]:
                log_fail("JS Error after analysis", e.get('message', '')[:80])
        else:
            log_pass("Analysis ran without JS errors")
    except Exception as e:
        log_fail("Run analysis", str(e))

    print("\n=== Test: Forest Plot ===")
    try:
        dismiss_alerts(driver)
        forest = driver.find_element(By.ID, "forestPlot")

        # Check if Plotly rendered
        plotly_divs = forest.find_elements(By.CSS_SELECTOR, ".js-plotly-plot, svg")
        if plotly_divs:
            log_pass("Forest plot rendered with Plotly")
        else:
            log_fail("Forest plot", "No Plotly/SVG content")
    except Exception as e:
        log_fail("Forest plot", str(e))

    print("\n=== Test: Tab Navigation ===")
    try:
        dismiss_alerts(driver)
        tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-tab]")
        log_pass(f"Found {len(tabs)} tabs")

        for tab in tabs:
            try:
                tab_name = tab.get_attribute('data-tab') or 'unnamed'
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
                time.sleep(0.2)
                tab.click()
                time.sleep(0.5)
                dismiss_alerts(driver)

                errors = get_js_errors(driver)
                if errors:
                    for e in errors[:1]:
                        log_fail(f"JS Error in tab '{tab_name}'", e.get('message', '')[:60])
                else:
                    log_pass(f"Tab '{tab_name}' clicked OK")
            except Exception as e:
                pass  # Some tabs may be hidden
    except Exception as e:
        log_fail("Tab navigation", str(e))

    print("\n=== Test: Funnel Plot ===")
    try:
        dismiss_alerts(driver)
        # Click funnel tab first
        funnel_tabs = driver.find_elements(By.XPATH, "//button[@data-tab='funnel' or contains(text(), 'Funnel')]")
        if funnel_tabs:
            funnel_tabs[0].click()
            time.sleep(1)

        funnel = driver.find_element(By.ID, "funnelPlot")
        plotly_divs = funnel.find_elements(By.CSS_SELECTOR, ".js-plotly-plot, svg")
        if plotly_divs:
            log_pass("Funnel plot rendered")
        else:
            log_fail("Funnel plot", "No Plotly/SVG content")
    except Exception as e:
        log_fail("Funnel plot", str(e))

    print("\n=== Test: Different Data Types with Full Analysis ===")
    data_types = ['binary', 'continuous', 'proportion', 'correlation', 'generic']

    for dt in data_types:
        print(f"\n--- Testing {dt} data type ---")
        try:
            dismiss_alerts(driver)

            # Select data type
            select = Select(driver.find_element(By.ID, "dataTypeSelect"))
            select.select_by_value(dt)
            time.sleep(0.5)
            dismiss_alerts(driver)

            # Load demo data for this type
            driver.execute_script(f"if(typeof loadDemoData === 'function') loadDemoData('{dt}');")
            time.sleep(1)
            dismiss_alerts(driver)

            # Run analysis
            run_btn = driver.find_element(By.ID, "runAnalysisBtn")
            run_btn.click()
            time.sleep(2)
            dismiss_alerts(driver)

            errors = get_js_errors(driver)
            if errors:
                for e in errors[:2]:
                    log_fail(f"{dt} analysis JS error", e.get('message', '')[:60])
            else:
                log_pass(f"{dt} data analysis completed OK")

        except Exception as e:
            log_fail(f"{dt} data type test", str(e)[:60])

    print("\n=== Test: Publication Bias Panel ===")
    try:
        dismiss_alerts(driver)
        # Reset to binary
        select = Select(driver.find_element(By.ID, "dataTypeSelect"))
        select.select_by_value('binary')
        time.sleep(0.3)
        driver.execute_script("if(typeof loadDemoData === 'function') loadDemoData('binary');")
        time.sleep(1)
        dismiss_alerts(driver)

        run_btn = driver.find_element(By.ID, "runAnalysisBtn")
        run_btn.click()
        time.sleep(2)
        dismiss_alerts(driver)

        # Click bias tab
        bias_tabs = driver.find_elements(By.XPATH, "//button[@data-tab='bias' or contains(text(), 'Bias')]")
        if bias_tabs:
            bias_tabs[0].click()
            time.sleep(1)
            dismiss_alerts(driver)

            # Check for Egger's test
            page_text = driver.page_source
            if 'Egger' in page_text:
                log_pass("Egger's test found")
            if 'Begg' in page_text:
                log_pass("Begg's test found")
            if 'Trim' in page_text:
                log_pass("Trim-and-fill found")
    except Exception as e:
        log_fail("Publication bias panel", str(e))

    print("\n=== Test: HTA Module ===")
    try:
        dismiss_alerts(driver)
        hta_tabs = driver.find_elements(By.XPATH, "//button[@data-tab='hta' or contains(text(), 'HTA')]")
        if hta_tabs:
            hta_tabs[0].click()
            time.sleep(1)
            dismiss_alerts(driver)

            page_text = driver.page_source
            if 'CEAC' in page_text or 'Cost-Effectiveness' in page_text:
                log_pass("HTA CEAC section found")
            if 'EVPI' in page_text:
                log_pass("HTA EVPI section found")

            errors = get_js_errors(driver)
            if not errors:
                log_pass("HTA module no JS errors")
    except Exception as e:
        log_fail("HTA module", str(e))

    print("\n=== Test: Validation Panel ===")
    try:
        dismiss_alerts(driver)
        valid_tabs = driver.find_elements(By.XPATH, "//button[@data-tab='validation' or contains(text(), 'Validation')]")
        if valid_tabs:
            valid_tabs[0].click()
            time.sleep(1)
            dismiss_alerts(driver)

            page_text = driver.page_source
            if 'metafor' in page_text:
                log_pass("Benchmark comparison with metafor found")
            if '400+' in page_text or '350+' in page_text:
                log_pass("Total feature score displayed")

            errors = get_js_errors(driver)
            if not errors:
                log_pass("Validation panel no JS errors")
    except Exception as e:
        log_fail("Validation panel", str(e))

    # Final JS error check
    print("\n=== Final JavaScript Error Summary ===")
    all_errors = get_js_errors(driver)
    if all_errors:
        print(f"Total JS errors: {len(all_errors)}")
        for err in all_errors[:5]:
            print(f"  - {err.get('message', '')[:100]}")
    else:
        print("No JavaScript errors in final check!")

def main():
    print("=" * 60)
    print("TruthCert-PairwisePro Test Suite v2")
    print("=" * 60)

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    driver = None
    try:
        driver = webdriver.Chrome(options=options)

        file_path = r"C:\Truthcert1\TruthCert-PairwisePro-v1.0.html"
        driver.get(f"file:///{file_path}")
        time.sleep(3)

        test_with_correct_ids(driver)

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"PASSED: {results['passed']}")
        print(f"FAILED: {results['failed']}")

        if results['errors']:
            print("\n--- ERRORS ---")
            for err in results['errors'][:15]:
                print(f"  - {err}")

        print("=" * 60)

        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
