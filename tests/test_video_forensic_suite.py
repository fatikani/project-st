"""
Enhanced Test Suite for Digital Forensic Video Analysis Application
Includes regression tests, exploratory testing, and AI-powered bug detection
"""

import pytest
import unittest
import allure
import time
import json
import os
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utilities.teststatus import TestStatus
from base.basepage import BasePage
import test_data.testData as td
from faker import Faker
import requests
from pathlib import Path


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class VideoForensicTests(unittest.TestCase):
    """
    Comprehensive test suite for the digital forensic video analysis application
    """

    @pytest.fixture(autouse=True)
    def classSetup(self):
        self.ts = TestStatus(self.driver)
        self.base_url = td.testData("environment")
        self.fake = Faker()
        
    def setUp(self):
        """Set up test environment before each test"""
        # Navigate to application
        self.driver.get(self.base_url)
        self.login_if_required()
    
    def login_if_required(self):
        """Login to application if not already logged in"""
        try:
            # Check if we're on login page
            login_form = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            # Perform login
            self.driver.find_element(By.ID, "username").send_keys("admin")
            self.driver.find_element(By.ID, "password").send_keys("admin123")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "navbar-brand"))
            )
        except TimeoutException:
            # Already logged in or login not required
            pass

    @allure.story('User Authentication')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_user_login_valid_credentials(self):
        """Test user login with valid credentials"""
        with allure.step('Navigate to login page'):
            self.driver.get(f"{self.base_url}/logout")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        
        with allure.step('Enter valid credentials'):
            self.driver.find_element(By.ID, "username").send_keys("admin")
            self.driver.find_element(By.ID, "password").send_keys("admin123")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        with allure.step('Verify successful login'):
            dashboard = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "navbar-brand"))
            )
            self.ts.markFinal(dashboard.is_displayed(), "Login failed - dashboard not visible")

    @allure.story('User Authentication')
    @allure.severity(allure.severity_level.HIGH)
    def test_02_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        with allure.step('Navigate to login page'):
            self.driver.get(f"{self.base_url}/logout")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        
        with allure.step('Enter invalid credentials'):
            self.driver.find_element(By.ID, "username").send_keys("invalid_user")
            self.driver.find_element(By.ID, "password").send_keys("invalid_pass")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        with allure.step('Verify login failure message'):
            error_alert = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
            )
            self.ts.markFinal(error_alert.is_displayed(), "Error message not displayed for invalid login")

    @allure.story('Video Upload')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_03_video_upload_valid_file(self):
        """Test video upload with valid file format"""
        with allure.step('Navigate to upload page'):
            self.driver.get(f"{self.base_url}/upload")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "case_number"))
            )
        
        with allure.step('Fill upload form'):
            case_number = f"TEST-{self.fake.random_number(digits=6)}"
            self.driver.find_element(By.ID, "case_number").send_keys(case_number)
            
            # Create a test video file
            test_video_path = self.create_test_video()
            file_input = self.driver.find_element(By.ID, "video")
            file_input.send_keys(test_video_path)
        
        with allure.step('Submit upload form'):
            self.driver.find_element(By.ID, "uploadBtn").click()
        
        with allure.step('Verify upload success'):
            # Should be redirected to analysis page
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("/analyze/")
            )
            self.ts.markFinal(True, "Video upload successful")

    @allure.story('Video Upload')
    @allure.severity(allure.severity_level.HIGH)
    def test_04_video_upload_invalid_file_format(self):
        """Test video upload with invalid file format"""
        with allure.step('Navigate to upload page'):
            self.driver.get(f"{self.base_url}/upload")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "case_number"))
            )
        
        with allure.step('Try to upload invalid file'):
            case_number = f"TEST-{self.fake.random_number(digits=6)}"
            self.driver.find_element(By.ID, "case_number").send_keys(case_number)
            
            # Create a test text file
            test_file_path = self.create_test_text_file()
            file_input = self.driver.find_element(By.ID, "video")
            file_input.send_keys(test_file_path)
            
            self.driver.find_element(By.ID, "uploadBtn").click()
        
        with allure.step('Verify error message'):
            error_alert = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
            )
            self.ts.markFinal("Invalid file type" in error_alert.text, "Invalid file error not shown")

    @allure.story('Video Analysis')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_05_video_analysis_workflow(self):
        """Test complete video analysis workflow"""
        # First upload a video
        self.test_03_video_upload_valid_file()
        
        with allure.step('Wait for analysis to complete'):
            # Wait on analysis page
            analysis_title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h5"))
            )
            
            # Wait for analysis completion (check status every 5 seconds)
            max_wait_time = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                current_url = self.driver.current_url
                if "/results/" in current_url:
                    break
                time.sleep(5)
                self.driver.refresh()
        
        with allure.step('Verify analysis results'):
            # Should be on results page
            self.ts.markFinal("/results/" in self.driver.current_url, "Analysis did not complete")
            
            # Check for metadata section
            metadata_section = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Video Metadata')]")
            self.ts.markFinal(metadata_section.is_displayed(), "Metadata section not found")

    @allure.story('Navigation')
    @allure.severity(allure.severity_level.NORMAL)
    def test_06_navigation_menu_functionality(self):
        """Test navigation menu functionality"""
        with allure.step('Test Dashboard navigation'):
            dashboard_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Dashboard')]")
            dashboard_link.click()
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/")
            )
            self.ts.mark(self.driver.current_url.endswith("/"), "Dashboard navigation failed")
        
        with allure.step('Test Upload navigation'):
            upload_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Upload Video')]")
            upload_link.click()
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/upload")
            )
            self.ts.markFinal("/upload" in self.driver.current_url, "Upload navigation failed")

    @allure.story('User Interface')
    @allure.severity(allure.severity_level.NORMAL)
    def test_07_responsive_design(self):
        """Test responsive design on different screen sizes"""
        screen_sizes = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            with allure.step(f'Test {width}x{height} resolution'):
                self.driver.set_window_size(width, height)
                time.sleep(2)  # Wait for responsive changes
                
                # Check if navbar is present
                navbar = self.driver.find_element(By.CLASS_NAME, "navbar")
                self.ts.mark(navbar.is_displayed(), f"Navbar not visible at {width}x{height}")

    @allure.story('Performance')
    @allure.severity(allure.severity_level.NORMAL)
    def test_08_page_load_performance(self):
        """Test page load performance"""
        pages_to_test = [
            "/",
            "/upload",
            "/login"
        ]
        
        for page in pages_to_test:
            with allure.step(f'Test load time for {page}'):
                start_time = time.time()
                self.driver.get(f"{self.base_url}{page}")
                
                # Wait for page to be fully loaded
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                load_time = time.time() - start_time
                self.ts.mark(load_time < 5.0, f"Page {page} took {load_time:.2f}s to load (should be < 5s)")

    @allure.story('Security')
    @allure.severity(allure.severity_level.HIGH)
    def test_09_unauthorized_access_protection(self):
        """Test protection against unauthorized access"""
        with allure.step('Logout first'):
            self.driver.get(f"{self.base_url}/logout")
        
        protected_pages = [
            "/",
            "/upload",
            "/analyze/1",
            "/results/1"
        ]
        
        for page in protected_pages:
            with allure.step(f'Test unauthorized access to {page}'):
                self.driver.get(f"{self.base_url}{page}")
                
                # Should be redirected to login
                WebDriverWait(self.driver, 10).until(
                    EC.url_contains("/login")
                )
                self.ts.mark("/login" in self.driver.current_url, f"Unauthorized access allowed to {page}")

    @allure.story('Data Validation')
    @allure.severity(allure.severity_level.HIGH)
    def test_10_form_validation(self):
        """Test form validation"""
        with allure.step('Navigate to upload page'):
            self.driver.get(f"{self.base_url}/upload")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "case_number"))
            )
        
        with allure.step('Test empty case number validation'):
            # Try to submit without case number
            self.driver.find_element(By.ID, "uploadBtn").click()
            
            # Check for HTML5 validation
            case_number_field = self.driver.find_element(By.ID, "case_number")
            validation_message = case_number_field.get_attribute("validationMessage")
            self.ts.mark(validation_message != "", "Case number validation not working")

    # Helper methods
    def create_test_video(self):
        """Create a simple test video file"""
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        video_path = test_dir / "test_video.mp4"
        
        # Create a simple 5-second video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
        
        for i in range(100):  # 5 seconds at 20 FPS
            # Create a frame with changing color
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:, :, i % 3] = (i * 2) % 255
            out.write(frame)
        
        out.release()
        return str(video_path.absolute())
    
    def create_test_text_file(self):
        """Create a test text file for invalid upload testing"""
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        text_path = test_dir / "test_file.txt"
        with open(text_path, 'w') as f:
            f.write("This is a test text file, not a video.")
        
        return str(text_path.absolute())


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class ExploratoryTests(unittest.TestCase):
    """
    Exploratory testing scenarios for discovering edge cases and usability issues
    """

    @pytest.fixture(autouse=True)
    def classSetup(self):
        self.ts = TestStatus(self.driver)
        self.base_url = td.testData("environment")
        self.fake = Faker()

    @allure.story('Exploratory Testing')
    @allure.severity(allure.severity_level.NORMAL)
    def test_edge_case_discovery(self):
        """Discover edge cases through exploratory testing"""
        
        # Navigate to application
        self.driver.get(self.base_url)
        
        with allure.step('Test unusual user interactions'):
            # Try rapid clicking
            try:
                upload_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Upload Video')]"))
                )
                for _ in range(10):
                    upload_link.click()
                    time.sleep(0.1)
                    
                # Check if application remains stable
                self.ts.mark(self.driver.current_url is not None, "Application crashed during rapid clicking")
            except Exception as e:
                self.ts.mark(False, f"Error during rapid clicking test: {str(e)}")
        
        with allure.step('Test browser back/forward navigation'):
            try:
                self.driver.get(f"{self.base_url}/upload")
                self.driver.back()
                self.driver.forward()
                
                # Verify page is still functional
                self.ts.mark("upload" in self.driver.current_url, "Navigation state inconsistent")
            except Exception as e:
                self.ts.mark(False, f"Error during navigation test: {str(e)}")

    @allure.story('Exploratory Testing')
    @allure.severity(allure.severity_level.NORMAL)
    def test_accessibility_features(self):
        """Test accessibility features"""
        
        self.driver.get(self.base_url)
        
        with allure.step('Test keyboard navigation'):
            # Use Tab key to navigate
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            focusable_elements = []
            for _ in range(10):  # Tab through first 10 elements
                body.send_keys(Keys.TAB)
                active_element = self.driver.switch_to.active_element
                focusable_elements.append(active_element.tag_name)
                time.sleep(0.2)
            
            self.ts.mark(len(set(focusable_elements)) > 1, "Keyboard navigation not working properly")
        
        with allure.step('Check for alt attributes on images'):
            images = self.driver.find_elements(By.TAG_NAME, "img")
            images_with_alt = [img for img in images if img.get_attribute("alt")]
            
            if images:
                alt_percentage = len(images_with_alt) / len(images) * 100
                self.ts.mark(alt_percentage > 80, f"Only {alt_percentage:.1f}% of images have alt attributes")


class AIBugDetector:
    """
    AI-powered bug detection and classification system
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.detected_issues = []
    
    def analyze_page_for_bugs(self):
        """Analyze current page for potential bugs using AI heuristics"""
        issues = []
        
        # Check for JavaScript errors in console
        console_logs = self.driver.get_log('browser')
        for log in console_logs:
            if log['level'] == 'SEVERE':
                issues.append({
                    'type': 'JavaScript Error',
                    'severity': 'High',
                    'message': log['message'],
                    'timestamp': log['timestamp']
                })
        
        # Check for broken images
        broken_images = self.driver.execute_script("""
            var images = document.getElementsByTagName('img');
            var broken = [];
            for (var i = 0; i < images.length; i++) {
                if (!images[i].complete || images[i].naturalHeight == 0) {
                    broken.push(images[i].src);
                }
            }
            return broken;
        """)
        
        for img_src in broken_images:
            issues.append({
                'type': 'Broken Image',
                'severity': 'Medium',
                'message': f'Image not loading: {img_src}',
                'element': img_src
            })
        
        # Check for accessibility issues
        accessibility_issues = self.check_accessibility()
        issues.extend(accessibility_issues)
        
        # Check for performance issues
        performance_issues = self.check_performance()
        issues.extend(performance_issues)
        
        self.detected_issues.extend(issues)
        return issues
    
    def check_accessibility(self):
        """Check for common accessibility issues"""
        issues = []
        
        # Check for missing alt attributes
        images_without_alt = self.driver.execute_script("""
            var images = document.getElementsByTagName('img');
            var missing_alt = [];
            for (var i = 0; i < images.length; i++) {
                if (!images[i].alt || images[i].alt.trim() === '') {
                    missing_alt.push(images[i].outerHTML);
                }
            }
            return missing_alt;
        """)
        
        for img_html in images_without_alt:
            issues.append({
                'type': 'Accessibility Issue',
                'severity': 'Medium',
                'message': 'Image missing alt attribute',
                'element': img_html[:100] + '...' if len(img_html) > 100 else img_html
            })
        
        # Check for form labels
        inputs_without_labels = self.driver.execute_script("""
            var inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');
            var missing_labels = [];
            for (var i = 0; i < inputs.length; i++) {
                var input = inputs[i];
                var hasLabel = input.labels && input.labels.length > 0;
                var hasAriaLabel = input.getAttribute('aria-label');
                var hasAriaLabelledBy = input.getAttribute('aria-labelledby');
                
                if (!hasLabel && !hasAriaLabel && !hasAriaLabelledBy) {
                    missing_labels.push(input.outerHTML);
                }
            }
            return missing_labels;
        """)
        
        for input_html in inputs_without_labels:
            issues.append({
                'type': 'Accessibility Issue',
                'severity': 'High',
                'message': 'Form input missing label',
                'element': input_html[:100] + '...' if len(input_html) > 100 else input_html
            })
        
        return issues
    
    def check_performance(self):
        """Check for performance issues"""
        issues = []
        
        # Check page load time
        navigation_timing = self.driver.execute_script("""
            return window.performance.timing;
        """)
        
        if navigation_timing:
            load_time = (navigation_timing['loadEventEnd'] - navigation_timing['navigationStart']) / 1000
            if load_time > 5.0:
                issues.append({
                    'type': 'Performance Issue',
                    'severity': 'Medium',
                    'message': f'Page load time is {load_time:.2f}s (should be < 5s)',
                    'metric': load_time
                })
        
        # Check for large images
        large_images = self.driver.execute_script("""
            var images = document.getElementsByTagName('img');
            var large_imgs = [];
            for (var i = 0; i < images.length; i++) {
                var img = images[i];
                if (img.naturalWidth > 2000 || img.naturalHeight > 2000) {
                    large_imgs.push({
                        src: img.src,
                        width: img.naturalWidth,
                        height: img.naturalHeight
                    });
                }
            }
            return large_imgs;
        """)
        
        for img_info in large_images:
            issues.append({
                'type': 'Performance Issue',
                'severity': 'Low',
                'message': f'Large image detected: {img_info["width"]}x{img_info["height"]}',
                'element': img_info['src']
            })
        
        return issues
    
    def generate_bug_report(self):
        """Generate comprehensive bug report"""
        report = {
            'timestamp': time.time(),
            'url': self.driver.current_url,
            'total_issues': len(self.detected_issues),
            'issues_by_severity': {},
            'issues_by_type': {},
            'detailed_issues': self.detected_issues
        }
        
        # Categorize by severity
        for issue in self.detected_issues:
            severity = issue.get('severity', 'Unknown')
            if severity not in report['issues_by_severity']:
                report['issues_by_severity'][severity] = 0
            report['issues_by_severity'][severity] += 1
        
        # Categorize by type
        for issue in self.detected_issues:
            issue_type = issue.get('type', 'Unknown')
            if issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue_type] = 0
            report['issues_by_type'][issue_type] += 1
        
        return report


# Integration test for AI bug detection
@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class AIBugDetectionTests(unittest.TestCase):
    """
    Tests that integrate AI-powered bug detection
    """

    @pytest.fixture(autouse=True)
    def classSetup(self):
        self.ts = TestStatus(self.driver)
        self.base_url = td.testData("environment")
        self.ai_detector = AIBugDetector(self.driver)

    @allure.story('AI Bug Detection')
    @allure.severity(allure.severity_level.NORMAL)
    def test_ai_bug_detection_dashboard(self):
        """Run AI bug detection on dashboard page"""
        with allure.step('Navigate to dashboard'):
            self.driver.get(self.base_url)
            time.sleep(3)  # Wait for page to fully load
        
        with allure.step('Run AI bug detection'):
            issues = self.ai_detector.analyze_page_for_bugs()
            report = self.ai_detector.generate_bug_report()
        
        with allure.step('Analyze results'):
            # Log results
            allure.attach(
                json.dumps(report, indent=2),
                name="AI Bug Detection Report",
                attachment_type=allure.attachment_type.JSON
            )
            
            # Check for critical issues
            critical_issues = [issue for issue in issues if issue.get('severity') == 'High']
            self.ts.markFinal(
                len(critical_issues) == 0,
                f"Found {len(critical_issues)} critical issues on dashboard"
            )

    @allure.story('AI Bug Detection')
    @allure.severity(allure.severity_level.NORMAL)
    def test_ai_bug_detection_upload_page(self):
        """Run AI bug detection on upload page"""
        with allure.step('Navigate to upload page'):
            self.driver.get(f"{self.base_url}/upload")
            time.sleep(3)
        
        with allure.step('Run AI bug detection'):
            issues = self.ai_detector.analyze_page_for_bugs()
            report = self.ai_detector.generate_bug_report()
        
        with allure.step('Analyze results'):
            allure.attach(
                json.dumps(report, indent=2),
                name="Upload Page Bug Detection Report",
                attachment_type=allure.attachment_type.JSON
            )
            
            # Check for accessibility issues on form page
            accessibility_issues = [issue for issue in issues if issue.get('type') == 'Accessibility Issue']
            self.ts.markFinal(
                len(accessibility_issues) <= 2,  # Allow up to 2 minor accessibility issues
                f"Found {len(accessibility_issues)} accessibility issues on upload page"
            )