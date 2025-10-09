# Digital Forensic Video Analysis Platform - Streamlit Edition

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy Status](https://img.shields.io/badge/deploy-ready-brightgreen.svg)](https://streamlit.io/)

## 🎯 Project Overview

This is a **production-ready Streamlit application** for digital forensic video analysis with integrated test automation. Designed for rapid deployment and client demonstrations, featuring a minimalist interface and comprehensive forensic capabilities.

### 🌟 Key Features

#### Digital Forensic Video Analysis
- 🔍 **Advanced Video Analysis**: Metadata extraction, integrity verification, and digital signature validation
- 🎬 **Motion Detection**: AI-powered motion analysis with frame-by-frame examination
- 🔒 **Tampering Detection**: Machine learning algorithms to detect video manipulation
- 📊 **Quality Assessment**: Automated video quality and authenticity analysis
- 📈 **Comprehensive Reporting**: Detailed forensic analysis reports with visual charts

#### Test Automation Framework
- 🤖 **AI-Powered Bug Detection**: Machine learning-based bug classification and prediction
- 🧪 **Comprehensive Test Suite**: Functional, performance, security, and exploratory testing
- 📱 **Cross-Browser Testing**: Support for Chrome, Firefox, Safari, and Edge
- 📊 **Advanced Reporting**: Visual test reports with bug taxonomy and AI insights
- 🔄 **Regression Testing**: Automated regression test suites with CI/CD integration

#### AI Platform Integration
- 🧠 **Machine Learning Models**: Custom-trained models for bug prediction and video analysis
- ☁️ **Cloud AI Services**: Integration with OpenAI, Azure Cognitive Services, and AWS AI
- 📈 **Predictive Analytics**: Pattern recognition and anomaly detection
- 🎯 **Intelligent Recommendations**: AI-generated testing and quality improvement suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 8GB RAM (16GB recommended)
- Chrome/Firefox browser
- FFmpeg for video processing

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/digital-forensic-video-analysis.git
   cd digital-forensic-video-analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open browser: `http://localhost:5000`
   - Login: `admin` / `admin123`

## 🧪 Testing Framework

### Run Basic Tests
```bash
# Run all tests
pytest tests/ -v --allure-results allure-results

# Run specific test categories
pytest tests/test_video_forensic_suite.py -v

# Generate reports
allure serve allure-results
```

### Enhanced AI Testing
```bash
# Run AI-powered test analysis
pytest tests/test_video_forensic_suite.py::AIBugDetectionTests -v

# Generate enhanced reports
python utilities/enhanced_reporter.py
```
            self.elementClick(*self.locator(self.loginPage_locators, 'btn_login'))

* Then, in **test module**, create a new script for your test case(s) e.g: `test_login.py` and add your test case, as below:

        @allure.story('epic_1') # story of the test case
        @allure.severity(allure.severity_level.MINOR) # severity of the test case
        @pytestrail.case('C48') # test case id on test rail
        def test_login_successfully(self):

            with allure.step('Navigate to login page'): # name of the test step
                self.homeNavigation.goToLoginPage()
                self.ts.markFinal(self.loginPage.isAt, "navigation to login page failed") # check if the navigation to login page occurs successfully

            with allure.step('Login'): # name of the test step
                self.loginPage.login(email=td.testData("email"), password=td.testData("password"))
                self.ts.markFinal(self.dashboardPage.isAt, "login failed") # check if login successfully

**Notes:**

- use `@allure.story('[epic name]')` decorator before each test case to define the related epic / story.
- use `@allure.severity(allure.severity_level.[severity])` decorator before each test case to define the severity of the test case Minor/Major/Critical/Blocker.
- use `@pytestrail.case('[test case id on testrail]')` decorator before each test case to defione the related test case id on test rail to make the script update run status on test rail.

# Run the test case

In order to run the test case after creation, use on of the below commands:

- To run the test case and create allure report but without update the status run on TestRail:

`py.test --alluredir=allure_report tests/test_login.py`

`allure serve allure_report`

- To run the test case, create allure report and update the status of run on TestRail:

`py.test --alluredir=allure_report tests/test_login.py --testrail`

`allure serve allure_report`

**Note:**

- There are other options of run that you can search for them, as running all the test cases for specific epic/story or with specific severity

# Integration with TestRail

In order to setup the integration with TestRail, edit `testrail.cfg` with your testrail domain and credentials, as below:

        [API]
        url = https://[your testrail domain].testrail.io
        email = [testrail email]
        password = [testrail password]

        [TESTRUN]
        project_id = [project id]

========================
