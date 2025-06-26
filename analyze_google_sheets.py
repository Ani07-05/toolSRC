#!/usr/bin/env python3
"""
Script to analyze Google Sheets responses and understand the conditional form structure
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

def analyze_google_sheets():
    """Analyze the Google Sheets responses to understand the form structure"""
    
    # Google Sheets URL
    sheets_url = "https://docs.google.com/spreadsheets/d/121aOmMqbRzHo_SzblBsKoqq27Qow7-Rh_ozJlGcdMoQ/edit?resourcekey=&gid=1802305204#gid=1802305204"
    
    print("=== Google Sheets Analysis ===\n")
    print(f"Analyzing: {sheets_url}")
    
    # For now, let's create a manual analysis based on the form structure
    # In a real implementation, you would need Google Sheets API credentials
    
    print("\nSince we don't have API credentials, let's analyze the form structure manually:")
    
    # Based on the Google Form you provided, here's the conditional structure:
    form_structure = {
        "universal_sections": [
            "Timestamp",
            "Email Address", 
            "Applicant/Orginization Name",
            "Applicant Type (Can be more than one option)",
            "Gmail ID",
            "Phone Number (With country code)",
            "Complete Address",
            "Product Name ( Exact name you want to register for GI protection)",
            "Common/Local Names (All alternative names by which this product is known locally)",
            "Region of Origin",
            "State/Province (Primary state or province of production)",
            "Production Districts (List all districts involved in traditional production)",
            "Specific Geographic Boundaries [Exact boundaries of the geographical area (villages, taluks, coordinates if available)]",
            "Why is this product special to this region? (Explain the connection between geography and product uniqueness)",
            "Select Product Category"
        ],
        
        "conditional_sections": {
            "Agricultural Products": [
                "Crop/Plant Type (Scientific name and variety of the plant/crop)",
                "Physical Characteristics( Describe size, color, shape, texture of the agricultural product )",
                "Taste & Aroma Profile (Detailed description of taste, flavor, and aromatic properties)",
                "Nutritional Properties (Nutritional content, vitamins, minerals, and health benefits)",
                "Harvest Season [When is the product typically harvested? (months/seasons)]",
                "Soil Requirements (Specific soil type, pH, and conditions needed for cultivation)",
                "Climate Requirements ( Temperature, rainfall, humidity requirements for optimal growth )",
                "Traditional Growing Methods (Traditional cultivation practices passed down through generations)",
                "Seeds/Planting Material (Source and characteristics of traditional seeds or planting material used)",
                "Natural Pest Control (Traditional methods of pest and disease management)",
                "Post-Harvest Processing [Steps taken immediately after harvest (drying, cleaning, sorting)]",
                "Traditional Storage Methods ( How the product is traditionally stored and preserved)",
                "Quality Grading (Traditional methods of quality assessment and grading)",
                "Average Yield per Acre (Typical production quantity per unit area)",
                "Total Annual Production (Total quantity produced annually in the region)",
                "Number of Farmers Involved (Approximate number of farmers/producers in the region)",
                "Price Premium ( How much more does this product sell for compared to similar products from other regions?)",
                "Export Markets (Countries/regions where this product is exported)",
                "Farmer Income Impact (How has this product improved farmer incomes and livelihoods?)"
            ],
            
            "Food & Beverages": [
                "Food Category",
                "Main Ingredients (List all primary ingredients and their sources)",
                "Taste Profile (Detailed description of taste, texture, and sensory characteristics)",
                "Nutritional Benefits (Health benefits, nutritional content, medicinal properties if any)",
                "Shelf Life ( How long does the product stay fresh under normal conditions?)",
                "Traditional Recipe ( Detailed traditional recipe or preparation method )",
                "Secret/Special Techniques (Any unique techniques or secrets that make this product special)",
                "Traditional Equipment ( Special equipment, utensils, or tools used in preparation)",
                "Aging/Fermentation Process (If applicable, describe aging, fermentation, or curing processes)",
                "Quality Control in Preparation ( How is quality maintained during preparation?)",
                "Local Raw Materials (Which ingredients must come from the specific geographical region?)",
                "Seasonal Availability (How does seasonality affect availability of ingredients and production?)",
                "Traditional Suppliers (Who are the traditional suppliers of raw materials?)",
                "Festival/Ceremonial Use (Is this food associated with specific festivals, ceremonies, or cultural events?)",
                "Traditional Consumption Patterns  (How and when is this food traditionally consumed?)",
                "Cultural Stories/Legends (Any cultural stories, legends, or folklore associated with this food)",
                "Daily/Monthly Production  (Typical production quantities per day or month)",
                "Number of Traditional Producers (How many families/businesses are involved in traditional production?)",
                "Market Reach (Local, regional, national, or international market presence)"
            ],
            
            "Handicrafts & Artisanal Products": [
                "Type of Handicraft",
                "Product Dimensions (Typical size and dimensions of the finished product)",
                "Materials Used  (All raw materials used and their local sources)",
                "Distinctive Design Features (What makes the design unique to this region?)",
                "Functional Use ( How is this product used in daily life or special occasions?)",
                "Manufacturing Process (Step-by-step description of the traditional making process)",
                "Special Tools & Equipment (Traditional tools and equipment used by artisans)",
                "Skill Requirements (What specific skills and training do artisans need?)",
                "Time to Create (How long does it take to create one piece?)",
                "Design Patterns/Motifs (Traditional patterns, motifs, or designs that are characteristic of the region)",
                "Number of Active Artisans (How many artisans are currently practicing this craft?)",
                "Community Background ( Which communities/families have traditionally practiced this craft?)",
                "Skill Transfer Method (How are skills passed down to new generations?)",
                "Training Period (How long does it take to train a new artisan?)",
                "Historical Significance (Historical importance and cultural significance of this craft)",
                "Traditional Uses in Society  (How was/is this product used in traditional society?)",
                "Symbolic Meaning (Any symbolic or spiritual significance of the craft)",
                "Production Capacity (How many pieces can an artisan produce per month?)",
                "Price Range  (Typical price range for different sizes/types)",
                "Market Challenges ( What challenges do artisans face in marketing their products?)"
            ],
            
            "Textiles & Fabrics": [
                "Type of Textile*",
                "Fiber Type (Thread count, weight, dimensions, thickness specifications)",
                "Color Palette (Traditional colors used and sources of natural dyes)",
                "Pattern/Design Characteristics (Distinctive patterns, motifs, or design elements)",
                "Traditional Loom Type ( Type of loom used and its characteristics)",
                "Weaving Technique ( Specific weaving techniques and methods used)",
                "Thread Preparation (How are threads prepared, spun, and treated before weaving?)",
                "Dyeing Process (Traditional dyeing methods and natural dye sources)",
                "Time to Complete ( How long does it take to complete one piece?)",
                "Weaver Community ( Which communities have traditionally practiced this weaving?)",
                "Number of Active Weavers (Current number of practicing weavers)",
                "Skill Complexity (Level of skill required and training needed)",
                "Design Creation Process (How are traditional designs created and modified?)",
                "Traditional Uses (How is this textile traditionally used in society?)",
                "Ceremonial Significance (Use in weddings, festivals, or religious ceremonies)",
                "Social Status Indicators ( Does this textile indicate social status or community membership?)",
                "Production per Weaver (Average monthly production per weaver)",
                "Raw Material Costs ( Cost and availability of raw materials)",
                "Market Demand ( Current market demand and customer base)"
            ],
            
            "Natural Products & Extracts": [
                "Product Type",
                "Source Plant/Material (Scientific name and description of source plant or natural material)",
                "Active Compounds (Key chemical compounds or active ingredients)",
                "Physical Properties (Color, consistency, aroma, and physical characteristics)",
                "Traditional Uses (How has this product been traditionally used?)",
                "Collection Season [ When is the raw material collected? (months/seasons)]",
                "Collection Methods  (Traditional methods of collection or harvesting)",
                "Processing Technique (How is the final product extracted or processed?)",
                "Traditional Equipment (Tools and equipment used in traditional processing)",
                "Quality Assessment (How is quality determined and maintained?)",
                "Habitat Requirements (Specific environmental conditions needed for the source material)",
                "Sustainable Practices (Traditional conservation and sustainability practices)",
                "Seasonal Variations ( How do seasonal changes affect product quality?)",
                "Geographic Specificity (Why can this product only be obtained from this specific region?)",
                "Indigenous Knowledge (Traditional knowledge systems associated with this product)",
                "Community Guardians ( Which communities have traditionally been guardians of this knowledge?)",
                "Traditional Applications (Detailed traditional uses in medicine, cosmetics, or daily life)",
                "Yield per Collection ( Typical quantity obtained per collection/processing cycle)",
                "Market Applications ( Modern commercial applications and uses)",
                "Value Addition Potential (Opportunities for processing into higher-value products)"
            ]
        },
        
        "universal_closing_sections": [
            "Production History (How long has this product been made in this region?)",
            "Historical Documents (Any historical references, documents, or evidence)",
            "Cultural Evolution  (How has production evolved while maintaining traditional character?)",
            "Producer Income (Average annual income per producer from this product )",
            "Employment Generation (Number of people employed directly and indirectly)",
            "Regional Economic Impact (Overall economic contribution to the region)",
            "Current Challenges (Main challenges facing production and marketing)",
            "Growth Potential (Potential for expanding production and markets)",
            "Support Needed ( What support is needed for development?)",
            "Product Photos ( High-quality photos of the product)",
            "Production Process Photos (Photos showing production/making process)",
            "Supporting Documents (Any certificates, awards, research papers, or other evidence)",
            "Applicant Declaration",
            "Unique Application ID [Enter a unique identifier for your application (used for file naming)]"
        ]
    }
    
    # Save the form structure for reference
    with open("form_structure_analysis.json", "w", encoding="utf-8") as f:
        json.dump(form_structure, f, indent=2, ensure_ascii=False)
    
    print("✓ Form structure analysis saved to form_structure_analysis.json")
    
    # Print summary
    print(f"\nForm Structure Summary:")
    print(f"- Universal sections: {len(form_structure['universal_sections'])}")
    print(f"- Conditional sections: {len(form_structure['conditional_sections'])} categories")
    print(f"- Universal closing sections: {len(form_structure['universal_closing_sections'])}")
    
    for category, fields in form_structure['conditional_sections'].items():
        print(f"  - {category}: {len(fields)} fields")
    
    print(f"\nTotal possible fields: {len(form_structure['universal_sections']) + len(form_structure['universal_closing_sections']) + max(len(fields) for fields in form_structure['conditional_sections'].values())}")
    
    return form_structure

def create_updated_data_processor():
    """Create an updated data processor that handles conditional form fields"""
    
    print("\n=== Creating Updated Data Processor ===\n")
    
    # Read the form structure
    with open("form_structure_analysis.json", "r", encoding="utf-8") as f:
        form_structure = json.load(f)
    
    # Create a comprehensive field mapping
    field_mapping = {}
    
    # Map universal sections
    for field in form_structure['universal_sections']:
        field_mapping[field] = {
            'section': 'universal',
            'category': 'all'
        }
    
    # Map conditional sections
    for category, fields in form_structure['conditional_sections'].items():
        for field in fields:
            field_mapping[field] = {
                'section': 'conditional',
                'category': category
            }
    
    # Map universal closing sections
    for field in form_structure['universal_closing_sections']:
        field_mapping[field] = {
            'section': 'universal_closing',
            'category': 'all'
        }
    
    # Save field mapping
    with open("field_mapping.json", "w", encoding="utf-8") as f:
        json.dump(field_mapping, f, indent=2, ensure_ascii=False)
    
    print("✓ Field mapping saved to field_mapping.json")
    
    # Create updated data processor code
    updated_processor_code = '''
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
'''
    
    # Save the updated processor code
    with open("updated_conditional_processor.py", "w", encoding="utf-8") as f:
        f.write(updated_processor_code)
    
    print("✓ Updated conditional processor code saved to updated_conditional_processor.py")
    
    return updated_processor_code

if __name__ == "__main__":
    # Analyze the form structure
    form_structure = analyze_google_sheets()
    
    # Create updated data processor
    create_updated_data_processor()
    
    print("\n=== Analysis Complete ===")
    print("The conditional form structure has been analyzed and the data processor has been updated.")
    print("You can now use the updated processor to handle the conditional form fields properly.") 