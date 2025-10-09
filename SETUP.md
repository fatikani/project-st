# Digital Forensic Video Analysis Framework - Setup & Deployment Guide

## 🚀 Quick Start

This comprehensive guide will help you set up and deploy the Digital Forensic Video Analysis application with integrated test automation framework.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Testing Framework Setup](#testing-framework-setup)
6. [Deployment](#deployment)
7. [GitHub Repository Setup](#github-repository-setup)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **Python**: 3.8 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 5GB free space
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+

### Required Software
- Python 3.8+
- pip (Python package manager)
- Git
- Google Chrome or Firefox (for Selenium testing)
- FFmpeg (for video processing)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/digital-forensic-video-analysis.git
cd digital-forensic-video-analysis
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

**Windows:**
- Download and install [FFmpeg](https://ffmpeg.org/download.html)
- Add FFmpeg to system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### 5. Download WebDriver

**Option 1: Automatic (Recommended)**
The framework uses webdriver-manager for automatic driver management.

**Option 2: Manual**
- Download [ChromeDriver](https://chromedriver.chromium.org/)
- Add to system PATH or place in project directory

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///forensic_db.sqlite

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=524288000  # 500MB

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-optional
AZURE_COGNITIVE_SERVICES_KEY=your-azure-key-optional

# Test Configuration
TEST_BASE_URL=http://localhost:5000
BROWSER=chrome
HEADLESS=False
IMPLICIT_WAIT=10
EXPLICIT_WAIT=30
```

### 2. Test Data Configuration

Update `test_data/test_data.json`:

```json
{
    "environment": "http://localhost:5000",
    "browser": "chrome",
    "email": "admin",
    "password": "admin123",
    "test_video_path": "test_files/sample_video.mp4",
    "max_wait_time": 30
}
```

### 3. Locators Configuration

Update `locators/locators.json` for any UI changes:

```json
[
    {
        "pageName": "LoginPage",
        "name": "input_username",
        "locateUsing": "id",
        "locator": "username"
    },
    {
        "pageName": "LoginPage",
        "name": "input_password",
        "locateUsing": "id",
        "locator": "password"
    },
    {
        "pageName": "DashboardPage",
        "name": "upload_button",
        "locateUsing": "xpath",
        "locator": "//a[contains(text(), 'Upload Video')]"
    }
]
```

## 🚀 Running the Application

### 1. Initialize Database

```bash
python app.py
```

This will create the SQLite database and default admin user.

### 2. Start the Web Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

**Default Login Credentials:**
- Username: `admin`
- Password: `admin123`

### 3. Verify Installation

1. Open browser and navigate to `http://localhost:5000`
2. Login with default credentials
3. Upload a test video file
4. Verify analysis completion

## 🧪 Testing Framework Setup

### 1. Install Test Dependencies

All test dependencies are included in `requirements.txt`. Verify installation:

```bash
python -c "import pytest, selenium, allure; print('Test dependencies installed successfully')"
```

### 2. Configure Browser Settings

**Chrome (Recommended):**
```python
# conftest.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_chrome_options():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")  # Uncomment for headless mode
    return options
```

### 3. Run Basic Tests

**Single Test:**
```bash
pytest tests/test_login.py::LoginTest::test_login_successfully -v
```

**Full Test Suite:**
```bash
pytest tests/ -v --allure-results allure-results
```

**Enhanced Test Suite with AI:**
```bash
pytest tests/test_video_forensic_suite.py -v --allure-results allure-results
```

### 4. Generate Test Reports

**Allure Report:**
```bash
allure serve allure-results
```

**Enhanced HTML Report:**
```bash
python utilities/enhanced_reporter.py
```

## 🚀 Deployment

### 1. Production Configuration

Update `.env` for production:

```env
SECRET_KEY=your-super-secret-production-key
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/forensic_db
```

### 2. Docker Deployment

**Create Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p uploads analysis_results test_reports

EXPOSE 5000

CMD ["python", "app.py"]
```

**Build and Run:**
```bash
docker build -t forensic-video-app .
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads forensic-video-app
```

### 3. Cloud Deployment (AWS/Azure/GCP)

**AWS EC2:**
1. Launch EC2 instance (t3.medium or larger)
2. Install Docker
3. Deploy using Docker Compose
4. Configure security groups for port 5000

**Azure Container Instances:**
```bash
az container create \
    --resource-group myResourceGroup \
    --name forensic-video-app \
    --image forensic-video-app:latest \
    --cpu 2 --memory 4 \
    --ports 5000
```

### 4. Reverse Proxy Setup (Nginx)

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 500M;
}
```

## 📁 GitHub Repository Setup

### 1. Create New Repository

```bash
# Create new repository on GitHub, then:
git remote add origin https://github.com/yourusername/project.git
git branch -M main
git push -u origin main
```

### 2. GitHub Actions CI/CD

**Create `.github/workflows/ci.yml`:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "Deploy to production server"
        # Add your deployment commands here
```

### 3. Repository Structure

```
digital-forensic-video-analysis/
├── .github/
│   └── workflows/
│       └── ci.yml
├── base/
├── locators/
├── navigation/
├── pages/
├── screenshots/
├── test_data/
├── tests/
├── utilities/
├── templates/
├── uploads/
├── app.py
├── requirements.txt
├── TEST_PLAN.md
├── README.md
├── .env.example
├── .gitignore
└── Dockerfile
```

### 4. Documentation Files

**Create comprehensive README.md:**

```markdown
# Digital Forensic Video Analysis Framework

## Features
- 🔍 Advanced video forensic analysis
- 🤖 AI-powered bug detection
- 📊 Comprehensive test reporting
- 🔒 Secure user authentication
- 📱 Responsive web interface

## Quick Start
See [SETUP.md](SETUP.md) for detailed installation instructions.

## Testing
Run the test suite:
```bash
pytest tests/ -v --allure-results allure-results
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT License
```

## 🔧 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # macOS/Linux
```

**2. Database Connection Issues**
```bash
# Reset database
rm forensic_db.sqlite
python app.py  # Will recreate database
```

**3. Video Processing Errors**
```bash
# Verify FFmpeg installation
ffmpeg -version

# Check video file format
ffprobe your_video.mp4
```

**4. Selenium WebDriver Issues**
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager

# Run in headless mode
export HEADLESS=True  # Linux/macOS
set HEADLESS=True     # Windows
```

**5. Memory Issues During Testing**
```bash
# Reduce parallel test execution
pytest tests/ -v --numprocesses=2

# Run specific test categories
pytest tests/test_login.py -v
```

### Performance Optimization

**1. Database Optimization**
- Use PostgreSQL for production
- Enable database connection pooling
- Add appropriate indexes

**2. Video Processing Optimization**
- Use GPU acceleration if available
- Implement video chunking for large files
- Add caching for frequently accessed results

**3. Test Execution Optimization**
- Use parallel test execution
- Implement test data cleanup
- Use page object pattern effectively

## 📊 Monitoring and Logging

### Application Monitoring

**Add logging configuration:**

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/forensic_app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Test Monitoring

```bash
# Generate continuous test reports
pytest tests/ --html=reports/report.html --self-contained-html

# Monitor test execution time
pytest tests/ --benchmark-autosave --benchmark-histogram
```

## 🔐 Security Considerations

### Production Security Checklist

- [ ] Change default admin credentials
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS with SSL certificates
- [ ] Implement file upload validation
- [ ] Add rate limiting
- [ ] Enable CSRF protection
- [ ] Implement proper session management
- [ ] Add input sanitization
- [ ] Configure secure headers
- [ ] Regular security updates

### File Upload Security

```python
# Add to app.py
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Virus scanning (optional)
def scan_file_for_viruses(file_path):
    # Implement virus scanning logic
    pass
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run test suite: `pytest tests/ -v`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Create Pull Request

### Code Style

Use Black for code formatting:
```bash
pip install black
black .
```

### Testing Guidelines

- Write tests for new features
- Maintain >80% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/project/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/project/discussions)
- **Email**: support@yourproject.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for digital forensic professionals and QA engineers**