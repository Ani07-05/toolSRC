#!/usr/bin/env python3
"""
Test script to verify Google Sheets integration
"""

import os
import sys
from modules.data_processor import DataProcessor

def test_google_sheets_integration():
    """Test the Google Sheets integration"""
    
    print("🧪 Testing Google Sheets Integration...")
    print("-" * 50)
    
    # Test spreadsheet ID (from the provided URL)
    spreadsheet_id = "121aOmMqbRzHo_SzblBsKoqq27Qow7-Rh_ozJlGcdMoQ"
    
    try:
        # Initialize data processor
        print("📊 Initializing data processor...")
        data_processor = DataProcessor()
        
        # Process Google Sheets data
        print(f"📋 Fetching data from spreadsheet: {spreadsheet_id}")
        processed_data = data_processor.process_google_sheets_data(spreadsheet_id)
        
        # Display results
        print("\n✅ Successfully connected to Google Sheets!")
        print(f"📈 Total responses found: {processed_data['total_responses']}")
        
        # Show latest response summary
        latest = processed_data['latest_response']
        print("\n📝 Latest Response Summary:")
        print(f"  - Product Name: {latest.get(' Product Name ( Exact name you want to register for GI protection)', 'N/A')}")
        print(f"  - Region: {latest.get(' Region of Origin', 'N/A')}")
        print(f"  - Category: {latest.get('Select Product Category \n\nChoose the category that best describes your product', 'N/A')}")
        print(f"  - Applicant: {latest.get('Applicant/Orginization Name', 'N/A')}")
        
        # Test section data extraction
        sections_data = data_processor.extract_paper_sections_data(processed_data)
        print("\n📚 Paper Sections Prepared:")
        for section, data in sections_data.items():
            non_empty_fields = sum(1 for v in data.values() if v)
            print(f"  - {section}: {non_empty_fields} fields with data")
        
        print("\n🎉 All tests passed! Google Sheets integration is working correctly.")
        
    except FileNotFoundError as e:
        print(f"\n❌ Google credentials not found!")
        print(f"📁 Please create the credentials file at: config/google_credentials.json")
        print(f"📖 See config/GOOGLE_SHEETS_SETUP.md for instructions")
        return False
        
    except PermissionError as e:
        print(f"\n❌ Permission denied!")
        print(f"🔐 Please share the Google Sheet with the service account email")
        print(f"📧 The service account email should be shown in the error message above")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run the test
    success = test_google_sheets_integration()
    sys.exit(0 if success else 1) 