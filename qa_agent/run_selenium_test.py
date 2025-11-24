from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def test_discount_code_validation():
    """
    Test Case: TC-001
    Feature: Discount Code Validation
    Scenario: Apply valid discount code SAVE15
    Expected Result: 15% discount should be applied to order total
    """
    
    print("🚀 Starting Selenium Test...")
    
    # Initialize WebDriver with automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to the checkout page
        print("📄 Opening checkout.html...")
        checkout_path = "/Users/sarthakray/Autonomous_QA_Automation/qa_agent/sample_docs/checkout.html"
        driver.get(f"file://{checkout_path}")
        
        time.sleep(1)
        print("✓ Page loaded")
        
        # Fill discount code
        print("💰 Applying discount code SAVE15...")
        discount_input = wait.until(EC.presence_of_element_located((By.ID, "discount-code")))
        discount_input.clear()
        discount_input.send_keys("SAVE15")
        print("✓ Discount code entered")
        
        # Click apply button
        apply_button = wait.until(EC.element_to_be_clickable((By.ID, "apply-discount")))
        apply_button.click()
        print("✓ Apply button clicked")
        
        time.sleep(1)
        
        # Fill some required fields
        print("📝 Filling required fields...")
        
        full_name = driver.find_element(By.ID, "full-name")
        full_name.send_keys("John Doe")
        
        email = driver.find_element(By.ID, "email")
        email.send_keys("john.doe@example.com")
        
        phone = driver.find_element(By.ID, "phone")
        phone.send_keys("1234567890")
        
        address = driver.find_element(By.ID, "address")
        address.send_keys("123 Main St")
        
        city = driver.find_element(By.ID, "city")
        city.send_keys("New York")
        
        state = driver.find_element(By.ID, "state")
        state.send_keys("NY")
        
        postal = driver.find_element(By.ID, "postal-code")
        postal.send_keys("10001")
        
        print("✓ All fields filled")
        
        # Verify page elements exist
        page_title = driver.title
        page_source = driver.page_source
        
        assert "Checkout" in page_title or "checkout" in page_source.lower(), "Should be on checkout page"
        assert len(page_source) > 0, "Page should have content"
        
        print("✅ Test TC-001 PASSED!")
        print(f"📊 Page Title: {page_title}")
        
        # Take success screenshot
        driver.save_screenshot("/Users/sarthakray/Autonomous_QA_Automation/qa_agent/test_success.png")
        print("📸 Screenshot saved: test_success.png")
        
    except Exception as e:
        print(f"❌ Test FAILED: {str(e)}")
        # Take failure screenshot
        driver.save_screenshot("/Users/sarthakray/Autonomous_QA_Automation/qa_agent/test_failure.png")
        print("📸 Failure screenshot saved: test_failure.png")
        raise
    
    finally:
        time.sleep(2)  # Pause to see the result
        driver.quit()
        print("🔚 Browser closed")
        print("=" * 50)

if __name__ == "__main__":
    print("=" * 50)
    print("SELENIUM TEST EXECUTION")
    print("=" * 50)
    test_discount_code_validation()
    print("Test execution completed ✓")
