
# Updated data processor that handles conditional form fields
import pandas as pd
import json
import os
from typing import Dict, Any, List

class ConditionalFormProcessor:
    def __init__(self):
        self.field_mapping = self.load_field_mapping()
        self.form_structure = self.load_form_structure()
        
    def load_field_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load field mapping from JSON file"""
        try:
            with open("field_mapping.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def load_form_structure(self) -> Dict[str, Any]:
        """Load form structure from JSON file"""
        try:
            with open("form_structure_analysis.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def extract_conditional_data(self, row: pd.Series) -> Dict[str, Any]:
        """Extract data based on the selected product category"""
        product_category = row.get("Select Product Category", "")
        
        # Get the conditional fields for this category
        conditional_fields = self.form_structure.get('conditional_sections', {}).get(product_category, [])
        
        category_data = {}
        for field in conditional_fields:
            value = row.get(field, "")
            if pd.notna(value) and str(value).strip():
                # Convert field name to key format
                key = field.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("?", "").replace("/", "_").replace("&", "and")
                category_data[key] = str(value)
        
        return category_data
    
    def process_form_response(self, row: pd.Series) -> Dict[str, Any]:
        """Process a single form response with conditional fields"""
        
        # Extract universal data
        universal_data = {
            "applicant_info": {
                "applicant_name": row.get("Applicant/Orginization Name", ""),
                "applicant_type": row.get("Applicant Type (Can be more than one option)", ""),
                "gmail_id": row.get("Gmail ID", ""),
                "phone_number": row.get("Phone Number (With country code)", ""),
                "complete_address": row.get("Complete Address", "")
            },
            "product_info": {
                "product_name": row.get("Product Name ( Exact name you want to register for GI protection)", ""),
                "common_names": row.get("Common/Local Names (All alternative names by which this product is known locally)", "")
            },
            "geographic_info": {
                "region_of_origin": row.get("Region of Origin", ""),
                "state_province": row.get("State/Province (Primary state or province of production)", ""),
                "production_districts": row.get("Production Districts (List all districts involved in traditional production)", ""),
                "specific_boundaries": row.get("Specific Geographic Boundaries [Exact boundaries of the geographical area (villages, taluks, coordinates if available)]", ""),
                "geographic_connection": row.get("Why is this product special to this region? (Explain the connection between geography and product uniqueness)", "")
            },
            "product_category": row.get("Select Product Category", "")
        }
        
        # Extract conditional data based on product category
        category_data = self.extract_conditional_data(row)
        universal_data["category_specific_data"] = category_data
        
        # Extract universal closing data
        universal_data["historical_evidence"] = {
            "production_history": row.get("Production History (How long has this product been made in this region?)", ""),
            "historical_documents": row.get("Historical Documents (Any historical references, documents, or evidence)", ""),
            "cultural_evolution": row.get("Cultural Evolution  (How has production evolved while maintaining traditional character?)", "")
        }
        
        universal_data["economic_impact"] = {
            "producer_income": row.get("Producer Income (Average annual income per producer from this product )", ""),
            "employment_generation": row.get("Employment Generation (Number of people employed directly and indirectly)", ""),
            "regional_impact": row.get("Regional Economic Impact (Overall economic contribution to the region)", ""),
            "current_challenges": row.get("Current Challenges (Main challenges facing production and marketing)", ""),
            "growth_potential": row.get("Growth Potential (Potential for expanding production and markets)", ""),
            "support_needed": row.get("Support Needed ( What support is needed for development?)", "")
        }
        
        universal_data["supporting_documents"] = {
            "product_photos": row.get("Product Photos ( High-quality photos of the product)", ""),
            "process_photos": row.get("Production Process Photos (Photos showing production/making process)", ""),
            "supporting_docs": row.get("Supporting Documents (Any certificates, awards, research papers, or other evidence)", ""),
            "unique_id": row.get("Unique Application ID [Enter a unique identifier for your application (used for file naming)]", "")
        }
        
        return universal_data
