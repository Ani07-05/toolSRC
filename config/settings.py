import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets API Configuration
GOOGLE_CREDENTIALS_FILE = "config/google_credentials.json"
GOOGLE_SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

class Config:
    def __init__(self):
        self.config_file = "config/config.json"
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config = {
            "gemini_api_key": "",
            "output_directory": "output",
            "templates_directory": "templates",
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "supported_formats": [".xlsx", ".xls", ".csv"],
            "paper_template": "academic_paper_template.docx",
            "default_language": "en"
        }
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def validate_api_key(self, api_key):
        """Validate Gemini API key format"""
        if not api_key:
            return False, "API key cannot be empty"
        if len(api_key) < 20:
            return False, "API key seems too short"
        return True, "API key format appears valid"

# Global configuration instance
config = Config() 