#!/usr/bin/env python3
"""
Simple startup script for the GI Paper Writing Tool
"""

import os
import sys
import subprocess
import shutil

def check_poetry():
    """Check if Poetry is available"""
    return shutil.which("poetry") is not None

def install_requirements():
    """Install required packages using Poetry or pip"""
    if check_poetry():
        print("🎵 Poetry detected - using Poetry for dependency management")
        try:
            # Check if pyproject.toml exists in parent directory
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            pyproject_path = os.path.join(parent_dir, "pyproject.toml")
            
            if os.path.exists(pyproject_path):
                print("📦 Installing dependencies with Poetry...")
                os.chdir(parent_dir)
                subprocess.check_call(["poetry", "install"])
                print("✓ Dependencies installed successfully with Poetry")
                return True
            else:
                print("⚠️  pyproject.toml not found, falling back to pip")
        except subprocess.CalledProcessError as e:
            print(f"❌ Poetry installation failed: {e}")
            print("⚠️  Falling back to pip...")
    
    # Fallback to pip
    try:
        import flask
        import flask_cors
        print("✓ Required packages already installed")
    except ImportError:
        print("📦 Installing required packages with pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully with pip")
    
    return False

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
    using_poetry = install_requirements()
    
    # Check modules
    modules_available = check_modules()
    
    # Start the Flask server
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    if using_poetry:
        print("💡 Using Poetry - run 'poetry shell' in another terminal for development")
    
    print("-" * 50)
    
    # Import and run the server
    try:
        from server import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running:")
        if using_poetry:
            print("   poetry run python ui/server.py")
        else:
            print("   python server.py directly")

if __name__ == "__main__":
    main()
