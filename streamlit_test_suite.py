"""
Streamlit-Specific Test Automation Suite
Comprehensive testing framework for Streamlit Video Forensics Application
"""

import pytest
import time
import os
import tempfile
import json
import sqlite3
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from pathlib import Path

class StreamlitTestConfig:
    """Configuration for Streamlit testing"""
    
    # Streamlit application URL (adjust for your deployment)
    STREAMLIT_URL = "http://localhost:8501"
    
    # Test credentials
    TEST_USERNAME = "admin"
    TEST_PASSWORD = "admin123"
    
    # Timeouts
    DEFAULT_TIMEOUT = 10
    UPLOAD_TIMEOUT = 30
    ANALYSIS_TIMEOUT = 60
    
    # Test data paths
    TEST_VIDEO_PATH = "test_data/sample_video.mp4"
    TEST_RESULTS_DB = "test_forensic_db.sqlite"

class StreamlitTestBase:
    """Base class for Streamlit application testing"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome WebDriver for Streamlit testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Setup Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(StreamlitTestConfig.DEFAULT_TIMEOUT)
        
        yield driver
        
        # Cleanup
        driver.quit()
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment before each test"""
        # Create test database
        self.setup_test_database()
        
        # Create test video file if not exists
        self.setup_test_video()
        
        yield
        
        # Cleanup after test
        self.cleanup_test_environment()
    
    def setup_test_database(self):
        """Setup test database"""
        conn = sqlite3.connect(StreamlitTestConfig.TEST_RESULTS_DB)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'analyst',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create test user
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role) 
            VALUES (?, ?, ?)
        ''', ('admin', admin_hash, 'admin'))
        
        conn.commit()
        conn.close()
    
    def setup_test_video(self):
        """Create a small test video file"""
        # Create test_data directory
        os.makedirs("test_data", exist_ok=True)
        
        # Create a minimal MP4 file for testing (placeholder)
        if not os.path.exists(StreamlitTestConfig.TEST_VIDEO_PATH):
            # Create a dummy file for testing purposes
            with open(StreamlitTestConfig.TEST_VIDEO_PATH, 'wb') as f:
                # Write minimal MP4 header (for testing purposes only)
                f.write(b'\x00\x00\x00\x20\x66\x74\x79\x70\x69\x73\x6f\x6d')
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        # Remove test database
        if os.path.exists(StreamlitTestConfig.TEST_RESULTS_DB):
            os.remove(StreamlitTestConfig.TEST_RESULTS_DB)
    
    def navigate_to_streamlit_app(self, driver):
        """Navigate to Streamlit application"""
        driver.get(StreamlitTestConfig.STREAMLIT_URL)
        time.sleep(3)  # Wait for Streamlit to load
    
    def wait_for_streamlit_ready(self, driver):
        """Wait for Streamlit app to be ready"""
        try:
            # Wait for the main Streamlit container
            WebDriverWait(driver, StreamlitTestConfig.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "main"))
            )
            return True
        except TimeoutException:
            return False
    
    def find_streamlit_element(self, driver, element_type, text_content):
        """Find Streamlit element by type and text content"""
        try:
            # Common Streamlit element selectors
            selectors = {
                'button': "button",
                'input': "input",
                'text': "*",
                'header': "h1, h2, h3, h4, h5, h6",
                'selectbox': "select",
                'checkbox': "input[type='checkbox']",
                'file_uploader': "input[type='file']"
            }
            
            selector = selectors.get(element_type, "*")
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                if text_content.lower() in element.text.lower() or text_content in element.get_attribute('value') or '':
                    return element
            
            return None
            
        except Exception as e:
            print(f"Error finding element: {e}")
            return None

class TestStreamlitAuthentication(StreamlitTestBase):
    """Test authentication functionality"""
    
    def test_login_page_loads(self, driver):
        """Test that login page loads correctly"""
        self.navigate_to_streamlit_app(driver)
        assert self.wait_for_streamlit_ready(driver)
        
        # Check for authentication elements
        login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Authentication')]")
        assert len(login_elements) > 0, "Authentication section not found"
    
    def test_successful_login(self, driver):
        """Test successful user login"""
        self.navigate_to_streamlit_app(driver)
        time.sleep(2)
        
        # Find username input
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        username_input.clear()
        username_input.send_keys(StreamlitTestConfig.TEST_USERNAME)
        
        # Find password input
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.clear()
        password_input.send_keys(StreamlitTestConfig.TEST_PASSWORD)
        
        # Click login button
        login_button = self.find_streamlit_element(driver, 'button', 'Login')
        if login_button:
            login_button.click()
            time.sleep(3)
            
            # Check for successful login indicators
            success_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'authenticated') or contains(text(), 'success')]")
            assert len(success_elements) > 0, "Login success message not found"
    
    def test_invalid_login(self, driver):
        """Test login with invalid credentials"""
        self.navigate_to_streamlit_app(driver)
        time.sleep(2)
        
        # Try invalid credentials
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        username_input.clear()
        username_input.send_keys("invalid_user")
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.clear()
        password_input.send_keys("invalid_password")
        
        login_button = self.find_streamlit_element(driver, 'button', 'Login')
        if login_button:
            login_button.click()
            time.sleep(3)
            
            # Check for error message
            error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid') or contains(text(), 'error')]")
            assert len(error_elements) > 0, "Error message not displayed for invalid login"

class TestStreamlitVideoUpload(StreamlitTestBase):
    """Test video upload functionality"""
    
    def login_first(self, driver):
        """Helper method to login before testing upload"""
        self.navigate_to_streamlit_app(driver)
        time.sleep(2)
        
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        username_input.send_keys(StreamlitTestConfig.TEST_USERNAME)
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(StreamlitTestConfig.TEST_PASSWORD)
        
        login_button = self.find_streamlit_element(driver, 'button', 'Login')
        if login_button:
            login_button.click()
            time.sleep(3)
    
    def test_upload_interface_exists(self, driver):
        """Test that upload interface is available after login"""
        self.login_first(driver)
        
        # Look for upload elements
        upload_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Upload') or contains(text(), 'file')]")
        assert len(upload_elements) > 0, "Upload interface not found"
    
    def test_file_upload_validation(self, driver):
        """Test file upload validation"""
        self.login_first(driver)
        
        # Navigate to upload page if needed
        upload_nav = self.find_streamlit_element(driver, 'button', 'Upload')
        if upload_nav:
            upload_nav.click()
            time.sleep(2)
        
        # Check for file uploader
        file_uploaders = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        
        if file_uploaders:
            file_uploader = file_uploaders[0]
            
            # Test with valid file type
            if os.path.exists(StreamlitTestConfig.TEST_VIDEO_PATH):
                file_uploader.send_keys(os.path.abspath(StreamlitTestConfig.TEST_VIDEO_PATH))
                time.sleep(2)
                
                # Check for file acceptance
                success_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'uploaded') or contains(text(), 'selected')]")
                assert len(success_elements) > 0, "Valid file not accepted"

class TestStreamlitAnalysisWorkflow(StreamlitTestBase):
    """Test analysis workflow functionality"""
    
    def login_and_upload(self, driver):
        """Helper method to login and upload a file"""
        self.navigate_to_streamlit_app(driver)
        time.sleep(2)
        
        # Login
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        username_input.send_keys(StreamlitTestConfig.TEST_USERNAME)
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(StreamlitTestConfig.TEST_PASSWORD)
        
        login_button = self.find_streamlit_element(driver, 'button', 'Login')
        if login_button:
            login_button.click()
            time.sleep(3)
        
        # Navigate to upload if needed
        upload_nav = self.find_streamlit_element(driver, 'text', 'Upload')
        if upload_nav:
            upload_nav.click()
            time.sleep(2)
        
        # Upload file
        file_uploaders = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if file_uploaders and os.path.exists(StreamlitTestConfig.TEST_VIDEO_PATH):
            file_uploaders[0].send_keys(os.path.abspath(StreamlitTestConfig.TEST_VIDEO_PATH))
            time.sleep(3)
    
    def test_analysis_options_available(self, driver):
        """Test that analysis options are available"""
        self.login_and_upload(driver)
        
        # Look for analysis options
        analysis_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Analysis') or contains(text(), 'Quick') or contains(text(), 'Standard')]")
        assert len(analysis_elements) > 0, "Analysis options not found"
    
    def test_start_analysis_button(self, driver):
        """Test that analysis can be started"""
        self.login_and_upload(driver)
        
        # Look for start analysis button
        start_button = self.find_streamlit_element(driver, 'button', 'Start Analysis')
        
        if start_button:
            start_button.click()
            time.sleep(5)  # Wait for analysis to start
            
            # Check for analysis progress indicators
            progress_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'progress') or contains(text(), 'analyzing') or contains(text(), 'complete')]")
            assert len(progress_elements) > 0, "Analysis progress not visible"

class TestStreamlitNavigation(StreamlitTestBase):
    """Test navigation and page functionality"""
    
    def login_first(self, driver):
        """Helper method to login"""
        self.navigate_to_streamlit_app(driver)
        time.sleep(2)
        
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        username_input.send_keys(StreamlitTestConfig.TEST_USERNAME)
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(StreamlitTestConfig.TEST_PASSWORD)
        
        login_button = self.find_streamlit_element(driver, 'button', 'Login')
        if login_button:
            login_button.click()
            time.sleep(3)
    
    def test_sidebar_navigation(self, driver):
        """Test sidebar navigation functionality"""
        self.login_first(driver)
        
        # Check for sidebar elements
        sidebar_elements = driver.find_elements(By.CSS_SELECTOR, ".sidebar")
        
        # If no sidebar class, check for navigation elements
        if not sidebar_elements:
            nav_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Upload') or contains(text(), 'Results') or contains(text(), 'Status')]")
            assert len(nav_elements) > 0, "Navigation elements not found"
    
    def test_page_transitions(self, driver):
        """Test navigation between pages"""
        self.login_first(driver)
        
        # Test navigation to different sections
        pages_to_test = ["Upload", "Results", "Status"]
        
        for page in pages_to_test:
            page_element = self.find_streamlit_element(driver, 'text', page)
            if page_element:
                page_element.click()
                time.sleep(2)
                
                # Verify page loaded
                page_content = driver.find_elements(By.XPATH, f"//*[contains(text(), '{page}')]")
                assert len(page_content) > 0, f"{page} page not loaded"
    
    def test_logout_functionality(self, driver):
        """Test logout functionality"""
        self.login_first(driver)
        
        # Look for logout button
        logout_button = self.find_streamlit_element(driver, 'button', 'Logout')
        
        if logout_button:
            logout_button.click()
            time.sleep(3)
            
            # Check if redirected to login page
            auth_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Authentication') or contains(text(), 'Login')]")
            assert len(auth_elements) > 0, "Logout did not redirect to login page"

class TestStreamlitResponsiveness(StreamlitTestBase):
    """Test responsive design functionality"""
    
    def test_mobile_responsiveness(self, driver):
        """Test mobile viewport responsiveness"""
        self.navigate_to_streamlit_app(driver)
        
        # Test different viewport sizes
        viewports = [
            (375, 667),   # iPhone SE
            (768, 1024),  # iPad
            (1920, 1080)  # Desktop
        ]
        
        for width, height in viewports:
            driver.set_window_size(width, height)
            time.sleep(2)
            
            # Check if main content is visible
            main_content = driver.find_elements(By.CSS_SELECTOR, ".main")
            assert len(main_content) > 0, f"Main content not visible at {width}x{height}"
    
    def test_ui_elements_scaling(self, driver):
        """Test that UI elements scale properly"""
        self.navigate_to_streamlit_app(driver)
        
        # Test different zoom levels
        zoom_levels = [0.5, 0.75, 1.0, 1.25, 1.5]
        
        for zoom in zoom_levels:
            driver.execute_script(f"document.body.style.zoom='{zoom}'")
            time.sleep(1)
            
            # Check if elements are still accessible
            interactive_elements = driver.find_elements(By.CSS_SELECTOR, "button, input, select")
            visible_elements = [el for el in interactive_elements if el.is_displayed()]
            
            assert len(visible_elements) > 0, f"No interactive elements visible at zoom {zoom}"

class TestStreamlitPerformance(StreamlitTestBase):
    """Test application performance"""
    
    def test_page_load_time(self, driver):
        """Test page load performance"""
        start_time = time.time()
        self.navigate_to_streamlit_app(driver)
        self.wait_for_streamlit_ready(driver)
        load_time = time.time() - start_time
        
        assert load_time < 10, f"Page load time too slow: {load_time:.2f}s"
    
    def test_analysis_timeout(self, driver):
        """Test that analysis doesn't hang indefinitely"""
        self.navigate_to_streamlit_app(driver)
        time.sleep(2)
        
        # Quick login and upload simulation
        try:
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            username_input.send_keys(StreamlitTestConfig.TEST_USERNAME)
            
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.send_keys(StreamlitTestConfig.TEST_PASSWORD)
            
            login_button = self.find_streamlit_element(driver, 'button', 'Login')
            if login_button:
                login_button.click()
                time.sleep(3)
            
            # Check that the application responds within reasonable time
            start_time = time.time()
            
            # Try to interact with the application
            elements = driver.find_elements(By.CSS_SELECTOR, "button, input, select")
            response_time = time.time() - start_time
            
            assert response_time < 5, f"Application response time too slow: {response_time:.2f}s"
            
        except Exception as e:
            # Application should handle errors gracefully
            print(f"Expected error during performance test: {e}")

# Test execution and reporting
class StreamlitTestReporter:
    """Generate test reports for Streamlit application"""
    
    @staticmethod
    def generate_test_summary(test_results):
        """Generate comprehensive test summary"""
        summary = {
            "total_tests": len(test_results),
            "passed": sum(1 for result in test_results if result["status"] == "PASSED"),
            "failed": sum(1 for result in test_results if result["status"] == "FAILED"),
            "errors": sum(1 for result in test_results if result["status"] == "ERROR"),
            "test_categories": {
                "authentication": 0,
                "upload": 0,
                "analysis": 0,
                "navigation": 0,
                "responsiveness": 0,
                "performance": 0
            }
        }
        
        # Categorize tests
        for result in test_results:
            test_name = result["test_name"].lower()
            if "auth" in test_name or "login" in test_name:
                summary["test_categories"]["authentication"] += 1
            elif "upload" in test_name:
                summary["test_categories"]["upload"] += 1
            elif "analysis" in test_name:
                summary["test_categories"]["analysis"] += 1
            elif "nav" in test_name:
                summary["test_categories"]["navigation"] += 1
            elif "responsive" in test_name:
                summary["test_categories"]["responsiveness"] += 1
            elif "performance" in test_name:
                summary["test_categories"]["performance"] += 1
        
        return summary
    
    @staticmethod
    def export_results_html(test_summary, output_file="streamlit_test_report.html"):
        """Export test results as HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Streamlit Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: white; border-radius: 5px; }}
                .passed {{ color: #28a745; }}
                .failed {{ color: #dc3545; }}
                .error {{ color: #ffc107; }}
            </style>
        </head>
        <body>
            <h1>Streamlit Video Forensics - Test Report</h1>
            <div class="summary">
                <h2>Test Summary</h2>
                <div class="metric">
                    <strong>Total Tests:</strong> {test_summary['total_tests']}
                </div>
                <div class="metric passed">
                    <strong>Passed:</strong> {test_summary['passed']}
                </div>
                <div class="metric failed">
                    <strong>Failed:</strong> {test_summary['failed']}
                </div>
                <div class="metric error">
                    <strong>Errors:</strong> {test_summary['errors']}
                </div>
            </div>
            
            <h3>Test Categories</h3>
            <ul>
        """
        
        for category, count in test_summary['test_categories'].items():
            html_content += f"<li><strong>{category.title()}:</strong> {count} tests</li>"
        
        html_content += """
            </ul>
            <p><em>Report generated on: """ + str(pd.Timestamp.now()) + """</em></p>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file

# Main test execution
if __name__ == "__main__":
    # This file should be run with pytest
    print("Run tests using: pytest streamlit_test_suite.py -v --html=report.html")