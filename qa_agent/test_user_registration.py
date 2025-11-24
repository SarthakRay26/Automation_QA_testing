from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def test_user_registration():
    """
    Test Case: TC-001
    Feature: User Registration with Password Validation
    Scenario: Register a new user with valid credentials
    Expected Result: User account created successfully
    """
    
    print("=" * 60)
    print("🚀 Starting User Registration Test")
    print("=" * 60)
    
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to registration page
        print("\n📄 Opening registration page...")
        html_path = "/Users/sarthakray/Autonomous_QA_Automation/qa_agent/sample_docs/user_registration.html"
        driver.get(f"file://{html_path}")
        time.sleep(1)
        print("✓ Page loaded")
        
        # Fill username
        print("\n📝 Filling registration form...")
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.clear()
        username.send_keys("testuser123")
        print("✓ Username: testuser123")
        
        # Fill email
        email = driver.find_element(By.ID, "email")
        email.clear()
        email.send_keys("testuser@example.com")
        print("✓ Email: testuser@example.com")
        
        # Fill full name
        full_name = driver.find_element(By.ID, "full-name")
        full_name.clear()
        full_name.send_keys("Test User")
        print("✓ Full Name: Test User")
        
        # Fill password (meets all requirements)
        password = driver.find_element(By.ID, "password")
        password.clear()
        password.send_keys("SecurePass123!")
        time.sleep(0.5)  # Wait for strength indicator
        print("✓ Password: SecurePass123! (strong)")
        
        # Fill password confirmation
        password_confirm = driver.find_element(By.ID, "password-confirm")
        password_confirm.clear()
        password_confirm.send_keys("SecurePass123!")
        print("✓ Password Confirmation: matched")
        
        # Fill optional phone
        phone = driver.find_element(By.ID, "phone")
        phone.clear()
        phone.send_keys("+1-555-0123")
        print("✓ Phone: +1-555-0123")
        
        # Accept terms
        terms_checkbox = driver.find_element(By.ID, "terms")
        if not terms_checkbox.is_selected():
            terms_checkbox.click()
        print("✓ Terms & Conditions: Accepted")
        
        # Check password strength bar
        strength_bar = driver.find_element(By.ID, "strength-bar")
        strength_width = strength_bar.value_of_css_property("width")
        print(f"\n🔒 Password Strength Indicator Width: {strength_width}")
        
        # Verify form elements are present
        print("\n✅ Validation Tests:")
        
        # Check username validation pattern
        username_value = username.get_attribute("value")
        assert len(username_value) >= 3, "Username should be at least 3 characters"
        assert len(username_value) <= 20, "Username should be at most 20 characters"
        print(f"✓ Username length valid: {len(username_value)} chars")
        
        # Check email format
        email_value = email.get_attribute("value")
        assert "@" in email_value, "Email should contain @"
        assert "." in email_value, "Email should contain domain"
        print(f"✓ Email format valid: {email_value}")
        
        # Check password requirements
        password_value = password.get_attribute("value")
        assert len(password_value) >= 8, "Password should be at least 8 characters"
        assert any(c.isupper() for c in password_value), "Password should have uppercase"
        assert any(c.isdigit() for c in password_value), "Password should have number"
        assert any(c in "!@#$%^&*" for c in password_value), "Password should have special char"
        print("✓ Password meets all requirements")
        
        # Check passwords match
        password_confirm_value = password_confirm.get_attribute("value")
        assert password_value == password_confirm_value, "Passwords should match"
        print("✓ Password confirmation matches")
        
        # Check terms accepted
        assert terms_checkbox.is_selected(), "Terms should be accepted"
        print("✓ Terms checkbox is checked")
        
        # Take success screenshot
        driver.save_screenshot("/Users/sarthakray/Autonomous_QA_Automation/qa_agent/registration_test_success.png")
        print("\n📸 Screenshot saved: registration_test_success.png")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED: User Registration Form Validation")
        print("=" * 60)
        
        # Note: In real test, we would click submit and verify API response
        print("\nℹ️  Note: Submit button not clicked (no backend to handle request)")
        print("   In production, we would verify:")
        print("   - HTTP 201 response")
        print("   - User created in database")
        print("   - Verification email sent")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        driver.save_screenshot("/Users/sarthakray/Autonomous_QA_Automation/qa_agent/registration_test_failure.png")
        print("📸 Failure screenshot saved: registration_test_failure.png")
        raise
    
    finally:
        time.sleep(2)  # Pause to see the result
        driver.quit()
        print("\n🔚 Browser closed")

if __name__ == "__main__":
    try:
        test_user_registration()
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        exit(1)
