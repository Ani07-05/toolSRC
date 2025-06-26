#!/usr/bin/env python3
"""
Simple startup script for the GI Paper Writing Tool
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages if not already installed"""
    try:
        import flask
        import flask_cors
        print("✓ Required packages already installed")
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully")

def check_modules():
    """Check if the main modules are available"""
    print("🔍 Checking module availability...")
    
    modules_status = {}
    
    # Check data processor
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from modules.data_processor import DataProcessor
        modules_status['data_processor'] = True
        print("✓ Data processor module available")
    except ImportError as e:
        modules_status['data_processor'] = False
        print(f"⚠️  Data processor module not available: {e}")
    
    # Check academic generator
    try:
        from modules.academic_generator import AcademicGenerator
        modules_status['academic_generator'] = True
        print("✓ Academic generator module available")
    except ImportError as e:
        modules_status['academic_generator'] = False
        print(f"⚠️  Academic generator module not available: {e}")
    
    # Check PDF generator
    try:
        from modules.pdf_generator import generate_paper_pdf
        modules_status['pdf_generator'] = True
        print("✓ PDF generator module available")
    except ImportError as e:
        modules_status['pdf_generator'] = False
        print(f"⚠️  PDF generator module not available: {e}")
    
    all_available = all(modules_status.values())
    
    if all_available:
        print("🎉 All modules available - full functionality enabled!")
    else:
        print("⚠️  Some modules unavailable - using simulated mode")
        print("   The UI will work but paper generation will be simulated")
    
    return all_available

def main():
    print("🚀 Starting GI Paper Writing Tool...")
    
    # Install requirements
    install_requirements()
    
    # Check modules
    modules_available = check_modules()
    
    # Start the Flask server
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import and run the server
    try:
        from server import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: python server.py directly")

if __name__ == "__main__":
    main() 