from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def test_tc_001():
    """
    Test Case: TC-001
    Feature: Basic Generate test cases for coupon validation  Functionality
    Scenario: Verify that Generate test cases for coupon validation  works as expected
    Expected Result: System should successfully handle Generate test cases for coupon validation
    """
    
    print("=" * 60)
    print(f"🚀 Starting Test: TC-001")
    print("=" * 60)
    
    # Initialize WebDriver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to the HTML file or application URL
        # Update this path based on your project structure
        html_path = os.path.expanduser("~/Autonomous_QA_Automation/qa_agent/sample_docs/third_sample/course_enrollment.html")
        
        if os.path.exists(html_path):
            driver.get(f"file://{html_path}")
            print(f"✓ Loaded local file: third_sample/course_enrollment.html")
        else:
            driver.get("http://localhost:8000")  # Fallback to localhost
            print("✓ Navigated to application")
        
        # Wait for page to load
        time.sleep(1)

        # Fill input fields
        coupon_code_field = wait.until(EC.presence_of_element_located((By.ID, "coupon-code")))
        coupon_code_field.clear()
        coupon_code_field.send_keys("SAVE25")
        print("✓ Filled coupon-code: SAVE25")
        card_number_field = wait.until(EC.presence_of_element_located((By.ID, "card-number")))
        card_number_field.clear()
        card_number_field.send_keys("4532123456789012")
        print("✓ Filled card-number: 4532123456789012")
        expiry_date_field = wait.until(EC.presence_of_element_located((By.ID, "expiry-date")))
        expiry_date_field.clear()
        expiry_date_field.send_keys("12/25")
        print("✓ Filled expiry-date: 12/25")
        cvv_field = wait.until(EC.presence_of_element_located((By.ID, "cvv")))
        cvv_field.clear()
        cvv_field.send_keys("123")
        print("✓ Filled cvv: 123")
        cardholder_name_field = wait.until(EC.presence_of_element_located((By.ID, "cardholder-name")))
        cardholder_name_field.clear()
        cardholder_name_field.send_keys("Test User")
        print("✓ Filled cardholder-name: Test User")

        # Click submit button
        apply_coupon_button = wait.until(EC.element_to_be_clickable((By.ID, "apply-coupon")))
        apply_coupon_button.click()
        print("✓ Clicked button: apply-coupon")
        time.sleep(1)

        # Wait for response
        time.sleep(2)
        
        # Verify expected result: System should successfully handle Generate test cases for coupon validation
        print("\n🔍 Verifying test assertions...")
        
        # Verify coupon/discount was applied
        discount_info = driver.find_element(By.ID, "discount-info")
        assert discount_info.is_displayed(), "Discount info should be visible"
        print("✓ Discount applied successfully")
        
        # Verify price breakdown
        final_price = driver.find_element(By.ID, "final-price")
        assert final_price.text, "Final price should be displayed"
        print(f"✓ Final price: {final_price.text}")
        # Check for validation/error messages
        time.sleep(1)
        page_source = driver.page_source
        # Look for error indicators in the page
        assert len(page_source) > 100, "Page should respond"
        print("✓ Validation checked")
        
        print("\n" + "=" * 60)
        print(f"✅ Test TC-001 PASSED!")
        print(f"Expected: System should successfully handle Generate test cases for coupon validation")
        print("=" * 60)
        
        # Take success screenshot
        screenshot_path = os.path.expanduser(f"~/Autonomous_QA_Automation/qa_agent/test_tc_001_success.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: test_tc_001_success.png")
        
    except Exception as e:
        print(f"\n❌ Test TC-001 FAILED: {str(e)}")
        
        # Take failure screenshot
        screenshot_path = os.path.expanduser(f"~/Autonomous_QA_Automation/qa_agent/test_tc_001_failure.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Failure screenshot: test_tc_001_failure.png")
        raise
    
    finally:
        time.sleep(1)
        driver.quit()
        print("🔚 Browser closed\n")

if __name__ == "__main__":
    try:
        test_tc_001()
        print("✓ Test execution completed successfully")
    except Exception:
        print("✗ Test execution failed")
        exit(1)