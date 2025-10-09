#!/usr/bin/env python3
"""
Quick Setup and Test Runner Script
Automates the setup and testing process for the Digital Forensic Video Analysis Framework
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path

class FrameworkSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        
    def print_banner(self):
        """Print welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║            Digital Forensic Video Analysis Framework          ║
║                     Quick Setup & Test Runner                 ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Error: Python 3.8 or higher is required")
            print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
            
        print("🏗️  Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get path to Python executable in virtual environment"""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get path to pip executable in virtual environment"""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        pip_path = self.get_venv_pip()
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ Error: requirements.txt not found")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True, capture_output=True)
            
            # Install requirements
            result = subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], 
                                  check=True, capture_output=True, text=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
    
    def check_system_dependencies(self):
        """Check for required system dependencies"""
        print("🔍 Checking system dependencies...")
        
        # Check for FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            print("✅ FFmpeg found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  FFmpeg not found - some video processing features may not work")
            self.print_ffmpeg_installation_instructions()
    
    def print_ffmpeg_installation_instructions(self):
        """Print FFmpeg installation instructions"""
        instructions = {
            "windows": "Download from https://ffmpeg.org/download.html and add to PATH",
            "darwin": "Install with: brew install ffmpeg",
            "linux": "Install with: sudo apt-get install ffmpeg"
        }
        
        instruction = instructions.get(self.system, "Please install FFmpeg for your system")
        print(f"   Installation: {instruction}")
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating necessary directories...")
        directories = [
            "uploads",
            "analysis_results", 
            "test_reports",
            "screenshots",
            "logs",
            "test_files",
            "ai_models"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
        
        print("✅ Directories created")
    
    def create_test_config(self):
        """Create test configuration if it doesn't exist"""
        config_path = self.project_root / "test_data" / "test_data.json"
        
        if config_path.exists():
            print("✅ Test configuration already exists")
            return
        
        print("⚙️  Creating test configuration...")
        
        config = {
            "environment": "http://localhost:5000",
            "browser": "chrome",
            "email": "admin", 
            "password": "admin123",
            "max_wait_time": 30,
            "headless": False,
            "implicit_wait": 10,
            "explicit_wait": 30
        }
        
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Test configuration created")
    
    def run_application(self):
        """Start the Flask application"""
        print("🚀 Starting the web application...")
        python_path = self.get_venv_python()
        app_path = self.project_root / "app.py"
        
        if not app_path.exists():
            print("❌ Error: app.py not found")
            return False
        
        try:
            print("   Application starting at http://localhost:5000")
            print("   Press Ctrl+C to stop the application")
            subprocess.run([str(python_path), str(app_path)], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Application stopped by user")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running application: {e}")
            return False
        
        return True
    
    def run_tests(self, test_type="basic"):
        """Run tests"""
        print(f"🧪 Running {test_type} tests...")
        python_path = self.get_venv_python()
        
        test_commands = {
            "basic": [str(python_path), "-m", "pytest", "tests/test_login.py", "-v"],
            "comprehensive": [str(python_path), "-m", "pytest", "tests/", "-v", "--allure-results", "allure-results"],
            "ai": [str(python_path), "-m", "pytest", "tests/test_video_forensic_suite.py::AIBugDetectionTests", "-v"],
            "performance": [str(python_path), "-m", "pytest", "-k", "performance", "tests/", "-v"]
        }
        
        command = test_commands.get(test_type, test_commands["basic"])
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("✅ Tests completed successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Some tests failed")
            print(e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            return False
    
    def generate_test_report(self):
        """Generate test reports"""
        print("📊 Generating test reports...")
        python_path = self.get_venv_python()
        reporter_path = self.project_root / "utilities" / "enhanced_reporter.py"
        
        if reporter_path.exists():
            try:
                subprocess.run([str(python_path), str(reporter_path)], check=True)
                print("✅ Enhanced test report generated")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Could not generate enhanced report: {e}")
        
        # Try to generate Allure report
        try:
            subprocess.run(["allure", "serve", "allure-results"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Allure not found - install Allure for detailed reports")
    
    def main_menu(self):
        """Display main menu and handle user choices"""
        while True:
            print("\n" + "="*60)
            print("MAIN MENU - Choose an option:")
            print("="*60)
            print("1. 🏗️  Complete Setup (Fresh Installation)")
            print("2. 🚀 Start Web Application")
            print("3. 🧪 Run Basic Tests")
            print("4. 🔬 Run Comprehensive Tests")
            print("5. 🤖 Run AI-Powered Tests")
            print("6. ⚡ Run Performance Tests")
            print("7. 📊 Generate Test Reports")
            print("8. ❓ Show Help")
            print("9. 🚪 Exit")
            print("="*60)
            
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                self.complete_setup()
            elif choice == "2":
                self.run_application()
            elif choice == "3":
                self.run_tests("basic")
            elif choice == "4":
                self.run_tests("comprehensive")
            elif choice == "5":
                self.run_tests("ai")
            elif choice == "6":
                self.run_tests("performance")
            elif choice == "7":
                self.generate_test_report()
            elif choice == "8":
                self.show_help()
            elif choice == "9":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-9.")
    
    def complete_setup(self):
        """Perform complete setup"""
        print("\n🏗️  Starting complete setup process...")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Creating directories", self.create_directories),
            ("Creating test configuration", self.create_test_config),
        ]
        
        for step_name, step_function in steps:
            print(f"\n{step_name}...")
            if not step_function():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the web application (option 2)")
        print("2. Run tests to verify everything works (option 3)")
        print("3. Check the generated test reports")
        
        return True
    
    def show_help(self):
        """Show help information"""
        help_text = """
📖 HELP - Digital Forensic Video Analysis Framework

🎯 WHAT THIS FRAMEWORK DOES:
   • Provides a web-based video forensic analysis tool
   • Includes comprehensive test automation capabilities
   • Uses AI for bug detection and pattern analysis
   • Generates detailed test reports with visualizations

🚀 QUICK START:
   1. Run complete setup (option 1) - first time only
   2. Start the web application (option 2)
   3. Open browser to http://localhost:5000
   4. Login with admin/admin123
   5. Upload a video file to test analysis

🧪 TESTING OPTIONS:
   • Basic Tests: Login, navigation, basic functionality
   • Comprehensive: All test categories including security
   • AI-Powered: Machine learning bug detection
   • Performance: Load times, memory usage, scalability

📁 KEY FILES:
   • app.py - Main web application
   • tests/ - All test files
   • TEST_PLAN.md - Detailed test documentation
   • SETUP.md - Complete setup instructions
   • TESTING_INSTRUCTIONS.md - Testing guide

🔧 TROUBLESHOOTING:
   • If tests fail: Check browser installation
   • If video upload fails: Install FFmpeg
   • If AI tests fail: Check ML library installation
   • For other issues: Check logs/ directory

📞 SUPPORT:
   • Documentation: README.md and *.md files
   • Issues: Create GitHub issue for bugs
   • Questions: Check TESTING_INSTRUCTIONS.md

🎨 FEATURES INCLUDED:
   ✅ Video upload and analysis
   ✅ Motion detection algorithms
   ✅ Quality assessment tools
   ✅ Comprehensive test automation
   ✅ AI-powered bug detection
   ✅ Cross-browser testing
   ✅ Performance monitoring
   ✅ Security testing
   ✅ Detailed reporting
   ✅ CI/CD integration ready
        """
        print(help_text)

def main():
    setup = FrameworkSetup()
    setup.print_banner()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup.complete_setup()
        elif command == "run":
            setup.run_application()
        elif command == "test":
            test_type = sys.argv[2] if len(sys.argv) > 2 else "basic"
            setup.run_tests(test_type)
        elif command == "report":
            setup.generate_test_report()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, run, test [basic|comprehensive|ai|performance], report")
    else:
        # Interactive mode
        setup.main_menu()

if __name__ == "__main__":
    main()