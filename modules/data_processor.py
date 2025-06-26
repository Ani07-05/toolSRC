#!/usr/bin/env python3
"""
Data Processor Module for GI Paper Writing Tool
Handles Google Sheets integration and data processing
"""

import os
import json
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, List, Any, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_SCOPES

class GoogleSheetsProcessor:
    """Handles Google Sheets data extraction and processing"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self._initialize_google_sheets()
    
    def _initialize_google_sheets(self):
        """Initialize Google Sheets API connection"""
        try:
            if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                raise FileNotFoundError(f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
            
            self.creds = Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_FILE, 
                scopes=GOOGLE_SHEETS_SCOPES
            )
            self.service = build('sheets', 'v4', credentials=self.creds)
            print("✅ Google Sheets API initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets API: {str(e)}")
            raise
    
    def get_form_responses(self, spreadsheet_id: str, sheet_name: str = "Form Responses 1") -> pd.DataFrame:
        """Extract form responses from Google Sheets"""
        try:
            # Get the sheet data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                raise ValueError("No data found in the sheet")
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            print(f"✅ Successfully loaded {len(df)} form responses")
            return df
            
        except HttpError as e:
            if e.resp.status == 403:
                raise PermissionError(f"Access denied. Please share the spreadsheet with: {self.creds.service_account_email}")
            else:
                raise Exception(f"Google Sheets API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading form responses: {str(e)}")
    
    def analyze_form_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the form structure and identify field categories"""
        structure = {
            'universal_fields': [],
            'category_specific_fields': {},
            'total_responses': len(df),
            'columns': list(df.columns)
        }
        
        # Analyze each column
        for col in df.columns:
            # Check if column contains category-specific data
            non_empty_values = df[col].dropna()
            unique_values = non_empty_values.unique()
            
            if len(unique_values) <= 5 and len(non_empty_values) < len(df) * 0.8:
                # Likely a category field
                structure['category_specific_fields'][col] = {
                    'unique_values': unique_values.tolist(),
                    'non_empty_count': len(non_empty_values)
                }
            else:
                # Likely a universal field
                structure['universal_fields'].append(col)
        
        return structure

class DataProcessor:
    """Main data processor for GI paper generation"""
    
    def __init__(self):
        self.sheets_processor = GoogleSheetsProcessor()
    
    def process_google_sheets_data(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Process data from Google Sheets and prepare for AI generation"""
        try:
            # Get form responses
            df = self.sheets_processor.get_form_responses(spreadsheet_id)
            
            # Analyze structure
            structure = self.sheets_processor.analyze_form_structure(df)
            
            # Process the latest response (most recent)
            latest_response = df.iloc[-1].to_dict()
            
            # Prepare data for AI generation
            processed_data = {
                'form_structure': structure,
                'latest_response': latest_response,
                'all_responses': df.to_dict('records'),
                'total_responses': len(df)
            }
            
            print(f"✅ Processed {len(df)} form responses")
            print(f"📊 Form structure analyzed: {len(structure['universal_fields'])} universal fields, {len(structure['category_specific_fields'])} category-specific fields")
            
            return processed_data
            
        except Exception as e:
            print(f"❌ Error processing Google Sheets data: {str(e)}")
            raise
    
    def extract_paper_sections_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data organized by paper sections based on actual form structure"""
        response = processed_data['latest_response']
        
        # Map form fields to paper sections based on actual form structure
        sections_data = {
            'abstract': {
                'gi_name': response.get(' Product Name ( Exact name you want to register for GI protection)', ''),
                'category': response.get('Select Product Category \n\nChoose the category that best describes your product', ''),
                'region': response.get(' Region of Origin', ''),
                'description': response.get(' Physical Characteristics( Describe size, color, shape, texture of the agricultural product )', ''),
                'significance': response.get('Why is this product special to this region? (Explain the connection between geography and product uniqueness)', '')
            },
            'introduction': {
                'gi_name': response.get(' Product Name ( Exact name you want to register for GI protection)', ''),
                'category': response.get('Select Product Category \n\nChoose the category that best describes your product', ''),
                'region': response.get(' Region of Origin', ''),
                'state_province': response.get(' State/Province (Primary state or province of production)', ''),
                'districts': response.get(' Production Districts (List all districts involved in traditional production)', ''),
                'geographic_boundaries': response.get('Specific Geographic Boundaries [Exact boundaries of the geographical area (villages, taluks, coordinates if available)]', ''),
                'historical_background': response.get(' Production History (How long has this product been made in this region?)', ''),
                'historical_documents': response.get(' Historical Documents (Any historical references, documents, or evidence)', ''),
                'significance': response.get('Why is this product special to this region? (Explain the connection between geography and product uniqueness)', '')
            },
            'literature_review': {
                'gi_name': response.get(' Product Name ( Exact name you want to register for GI protection)', ''),
                'category': response.get('Select Product Category \n\nChoose the category that best describes your product', ''),
                'traditional_uses': response.get('Traditional Uses in Society  (How was/is this product used in traditional society?)', ''),
                'cultural_significance': response.get(' Historical Significance (Historical importance and cultural significance of this craft)', ''),
                'symbolic_meaning': response.get('Symbolic Meaning (Any symbolic or spiritual significance of the craft)', ''),
                'cultural_stories': response.get('Cultural Stories/Legends (Any cultural stories, legends, or folklore associated with this food)', ''),
                'festival_use': response.get('Festival/Ceremonial Use (Is this food associated with specific festivals, ceremonies, or cultural events?)', '')
            },
            'methodology': {
                'gi_name': response.get(' Product Name ( Exact name you want to register for GI protection)', ''),
                'category': response.get('Select Product Category \n\nChoose the category that best describes your product', ''),
                'production_process': response.get(' Manufacturing Process (Step-by-step description of the traditional making process)', ''),
                'traditional_equipment': response.get('Traditional Equipment ( Special equipment, utensils, or tools used in preparation)', ''),
                'traditional_techniques': response.get('Secret/Special Techniques (Any unique techniques or secrets that make this product special)', ''),
                'quality_control': response.get('Quality Control in Preparation ( How is quality maintained during preparation?)', ''),
                'raw_materials': response.get(' Local Raw Materials (Which ingredients must come from the specific geographical region?)', ''),
                'traditional_suppliers': response.get('Traditional Suppliers (Who are the traditional suppliers of raw materials?)', '')
            },
            'results': {
                'gi_name': response.get(' Product Name ( Exact name you want to register for GI protection)', ''),
                'category': response.get('Select Product Category \n\nChoose the category that best describes your product', ''),
                'production_capacity': response.get(' Production Capacity (How many pieces can an artisan produce per month?)', ''),
                'annual_production': response.get('Total Annual Production (Total quantity produced annually in the region)', ''),
                'number_of_producers': response.get('Number of Traditional Producers (How many families/businesses are involved in traditional production?)', ''),
                'price_range': response.get('Price Range  (Typical price range for different sizes/types)', ''),
                'price_premium': response.get(' Price Premium ( How much more does this product sell for compared to similar products from other regions?)', ''),
                'export_markets': response.get('Export Markets (Countries/regions where this product is exported)', ''),
                'market_reach': response.get('Market Reach (Local, regional, national, or international market presence)', ''),
                'producer_income': response.get('Producer Income (Average annual income per producer from this product )', ''),
                'employment_generation': response.get(' Employment Generation (Number of people employed directly and indirectly)', ''),
                'regional_impact': response.get('Regional Economic Impact (Overall economic contribution to the region)', '')
            },
            'conclusion': {
                'gi_name': response.get(' Product Name ( Exact name you want to register for GI protection)', ''),
                'category': response.get('Select Product Category \n\nChoose the category that best describes your product', ''),
                'current_challenges': response.get(' Current Challenges (Main challenges facing production and marketing)', ''),
                'market_challenges': response.get('Market Challenges ( What challenges do artisans face in marketing their products?)', ''),
                'growth_potential': response.get('Growth Potential (Potential for expanding production and markets)', ''),
                'support_needed': response.get('Support Needed ( What support is needed for development?)', ''),
                'cultural_evolution': response.get('Cultural Evolution  (How has production evolved while maintaining traditional character?)', ''),
                'future_prospects': response.get('Growth Potential (Potential for expanding production and markets)', '')
            }
        }
        
        # Add category-specific data based on the selected category
        category = response.get('Select Product Category \n\nChoose the category that best describes your product', '').strip()
        
        if 'Agricultural' in category:
            # Add agricultural-specific fields
            sections_data['methodology'].update({
                'crop_type': response.get('Crop/Plant Type (Scientific name and variety of the plant/crop)', ''),
                'soil_requirements': response.get('Soil Requirements (Specific soil type, pH, and conditions needed for cultivation)', ''),
                'climate_requirements': response.get('Climate Requirements ( Temperature, rainfall, humidity requirements for optimal growth )', ''),
                'growing_methods': response.get('Traditional Growing Methods (Traditional cultivation practices passed down through generations)', ''),
                'seeds_material': response.get(' Seeds/Planting Material (Source and characteristics of traditional seeds or planting material used)', ''),
                'pest_control': response.get(' Natural Pest Control (Traditional methods of pest and disease management)', ''),
                'harvest_season': response.get('Harvest Season [When is the product typically harvested? (months/seasons)]', ''),
                'post_harvest': response.get(' Post-Harvest Processing [Steps taken immediately after harvest (drying, cleaning, sorting)]', ''),
                'storage_methods': response.get(' Traditional Storage Methods ( How the product is traditionally stored and preserved)', ''),
                'yield_per_acre': response.get(' Average Yield per Acre (Typical production quantity per unit area)', ''),
                'number_of_farmers': response.get('Number of Farmers Involved (Approximate number of farmers/producers in the region)', ''),
                'farmer_income_impact': response.get('Farmer Income Impact (How has this product improved farmer incomes and livelihoods?)', '')
            })
            
            sections_data['results'].update({
                'taste_aroma': response.get('Taste & Aroma Profile (Detailed description of taste, flavor, and aromatic properties)', ''),
                'nutritional_properties': response.get(' Nutritional Properties (Nutritional content, vitamins, minerals, and health benefits)', ''),
                'quality_grading': response.get('Quality Grading (Traditional methods of quality assessment and grading)', '')
            })
            
        elif 'Food' in category:
            # Add food-specific fields
            sections_data['methodology'].update({
                'main_ingredients': response.get('Main Ingredients (List all primary ingredients and their sources)', ''),
                'traditional_recipe': response.get('Traditional Recipe ( Detailed traditional recipe or preparation method )', ''),
                'aging_fermentation': response.get('Aging/Fermentation Process (If applicable, describe aging, fermentation, or curing processes)', ''),
                'seasonal_availability': response.get('Seasonal Availability (How does seasonality affect availability of ingredients and production?)', '')
            })
            
            sections_data['results'].update({
                'taste_profile': response.get('Taste Profile (Detailed description of taste, texture, and sensory characteristics)', ''),
                'nutritional_benefits': response.get('Nutritional Benefits (Health benefits, nutritional content, medicinal properties if any)', ''),
                'shelf_life': response.get(' Shelf Life ( How long does the product stay fresh under normal conditions?)', ''),
                'consumption_patterns': response.get(' Traditional Consumption Patterns  (How and when is this food traditionally consumed?)', ''),
                'daily_production': response.get(' Daily/Monthly Production  (Typical production quantities per day or month)', '')
            })
            
        elif 'Handicraft' in category:
            # Add handicraft-specific fields
            sections_data['methodology'].update({
                'materials_used': response.get(' Materials Used  (All raw materials used and their local sources)', ''),
                'special_tools': response.get('Special Tools & Equipment (Traditional tools and equipment used by artisans)', ''),
                'skill_requirements': response.get('Skill Requirements (What specific skills and training do artisans need?)', ''),
                'time_to_create': response.get('Time to Create (How long does it take to create one piece?)', ''),
                'skill_transfer': response.get(' Skill Transfer Method (How are skills passed down to new generations?)', ''),
                'training_period': response.get('Training Period (How long does it take to train a new artisan?)', '')
            })
            
            sections_data['results'].update({
                'product_dimensions': response.get(' Product Dimensions (Typical size and dimensions of the finished product)', ''),
                'design_features': response.get('Distinctive Design Features (What makes the design unique to this region?)', ''),
                'functional_use': response.get('Functional Use ( How is this product used in daily life or special occasions?)', ''),
                'design_patterns': response.get('Design Patterns/Motifs (Traditional patterns, motifs, or designs that are characteristic of the region)', ''),
                'number_of_artisans': response.get('Number of Active Artisans (How many artisans are currently practicing this craft?)', ''),
                'community_background': response.get(' Community Background ( Which communities/families have traditionally practiced this craft?)', '')
            })
            
        elif 'Textile' in category:
            # Add textile-specific fields
            sections_data['methodology'].update({
                'fiber_type': response.get('Fiber Type (Thread count, weight, dimensions, thickness specifications)', ''),
                'traditional_loom': response.get(' Traditional Loom Type ( Type of loom used and its characteristics)', ''),
                'weaving_technique': response.get('Weaving Technique ( Specific weaving techniques and methods used)', ''),
                'thread_preparation': response.get('Thread Preparation (How are threads prepared, spun, and treated before weaving?)', ''),
                'dyeing_process': response.get(' Dyeing Process (Traditional dyeing methods and natural dye sources) ', ''),
                'time_to_complete': response.get('Time to Complete ( How long does it take to complete one piece?)', '')
            })
            
            sections_data['results'].update({
                'color_palette': response.get(' Color Palette (Traditional colors used and sources of natural dyes)', ''),
                'pattern_characteristics': response.get('Pattern/Design Characteristics (Distinctive patterns, motifs, or design elements)', ''),
                'weaver_community': response.get('Weaver Community ( Which communities have traditionally practiced this weaving?)', ''),
                'number_of_weavers': response.get(' Number of Active Weavers (Current number of practicing weavers)', ''),
                'skill_complexity': response.get('Skill Complexity (Level of skill required and training needed)', ''),
                'design_creation': response.get(' Design Creation Process (How are traditional designs created and modified?)', ''),
                'traditional_uses': response.get('Traditional Uses (How is this textile traditionally used in society?)', ''),
                'ceremonial_significance': response.get('Ceremonial Significance (Use in weddings, festivals, or religious ceremonies)', ''),
                'social_status': response.get('Social Status Indicators ( Does this textile indicate social status or community membership?)', ''),
                'production_per_weaver': response.get(' Production per Weaver (Average monthly production per weaver)', ''),
                'raw_material_costs': response.get(' Raw Material Costs ( Cost and availability of raw materials)', ''),
                'market_demand': response.get(' Market Demand ( Current market demand and customer base) ', '')
            })
            
        elif 'Natural' in category:
            # Add natural product-specific fields
            sections_data['methodology'].update({
                'source_plant': response.get('Source Plant/Material (Scientific name and description of source plant or natural material)', ''),
                'collection_season': response.get('Collection Season [ When is the raw material collected? (months/seasons)]', ''),
                'collection_methods': response.get(' Collection Methods  (Traditional methods of collection or harvesting)', ''),
                'processing_technique': response.get('Processing Technique (How is the final product extracted or processed?)', ''),
                'traditional_equipment_natural': response.get('Traditional Equipment (Tools and equipment used in traditional processing)', ''),
                'quality_assessment': response.get(' Quality Assessment (How is quality determined and maintained?)', ''),
                'habitat_requirements': response.get(' Habitat Requirements (Specific environmental conditions needed for the source material)', ''),
                'sustainable_practices': response.get('Sustainable Practices (Traditional conservation and sustainability practices)', ''),
                'seasonal_variations': response.get('Seasonal Variations ( How do seasonal changes affect product quality?)', ''),
                'geographic_specificity': response.get('Geographic Specificity (Why can this product only be obtained from this specific region?)', ''),
                'indigenous_knowledge': response.get('Indigenous Knowledge (Traditional knowledge systems associated with this product)', ''),
                'community_guardians': response.get('Community Guardians ( Which communities have traditionally been guardians of this knowledge?)', ''),
                'traditional_applications': response.get('Traditional Applications (Detailed traditional uses in medicine, cosmetics, or daily life)', ''),
                'yield_per_collection': response.get('Yield per Collection ( Typical quantity obtained per collection/processing cycle)', '')
            })
            
            sections_data['results'].update({
                'active_compounds': response.get(' Active Compounds (Key chemical compounds or active ingredients)', ''),
                'physical_properties': response.get('Physical Properties (Color, consistency, aroma, and physical characteristics)', ''),
                'traditional_uses_natural': response.get('Traditional Uses (How has this product been traditionally used?)', ''),
                'market_applications': response.get(' Market Applications ( Modern commercial applications and uses)', ''),
                'value_addition': response.get('Value Addition Potential (Opportunities for processing into higher-value products)', '')
            })
        
        return sections_data

class GoogleFormProcessor:
    def __init__(self):
        self.supported_formats = config.get("supported_formats", [".xlsx", ".xls", ".csv"])
        self.data = None
        self.processed_data = {}
        
    def validate_file(self, file_path: str) -> tuple[bool, str]:
        """Validate uploaded file"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            return False, f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}"
        
        file_size = os.path.getsize(file_path)
        max_size = config.get("max_file_size", 100 * 1024 * 1024)
        if file_size > max_size:
            return False, f"File too large. Maximum size: {max_size // (1024*1024)}MB"
        
        return True, "File is valid"
    
    def load_data(self, file_path: str) -> tuple[bool, str]:
        """Load data from file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in [".xlsx", ".xls"]:
                self.data = pd.read_excel(file_path)
            elif file_ext == ".csv":
                self.data = pd.read_csv(file_path)
            else:
                return False, "Unsupported file format"
            
            return True, f"Successfully loaded {len(self.data)} rows of data"
            
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def extract_form_data(self) -> Dict[str, Any]:
        """Extract and structure form data"""
        if self.data is None or self.data.empty:
            return {}
        
        # Get the first row (assuming single response for now)
        row = self.data.iloc[0]
        
        # Extract data based on Google Form structure
        form_data = {
            "applicant_info": self._extract_applicant_info(row),
            "product_info": self._extract_product_info(row),
            "geographic_info": self._extract_geographic_info(row),
            "product_category": self._extract_product_category(row),
            "category_specific_data": self._extract_category_specific_data(row),
            "historical_evidence": self._extract_historical_evidence(row),
            "economic_impact": self._extract_economic_impact(row),
            "supporting_documents": self._extract_supporting_documents(row)
        }
        
        self.processed_data = form_data
        return form_data
    
    def _extract_applicant_info(self, row) -> Dict[str, str]:
        """Extract applicant information"""
        return {
            "applicant_name": str(row.get("Applicant/Orginization Name", "")),
            "applicant_type": str(row.get("Applicant Type (Can be more than one option)", "")),
            "gmail_id": str(row.get("Gmail ID", "")),
            "phone_number": str(row.get("Phone Number (With country code)", "")),
            "complete_address": str(row.get("Complete Address", ""))
        }
    
    def _extract_product_info(self, row) -> Dict[str, str]:
        """Extract basic product information"""
        return {
            "product_name": str(row.get("Product Name ( Exact name you want to register for GI protection)", "")),
            "common_names": str(row.get("Common/Local Names (All alternative names by which this product is known locally)", ""))
        }
    
    def _extract_geographic_info(self, row) -> Dict[str, str]:
        """Extract geographic information"""
        return {
            "region_of_origin": str(row.get("Region of Origin", "")),
            "state_province": str(row.get("State/Province (Primary state or province of production)", "")),
            "production_districts": str(row.get("Production Districts (List all districts involved in traditional production)", "")),
            "specific_boundaries": str(row.get("Specific Geographic Boundaries [Exact boundaries of the geographical area (villages, taluks, coordinates if available)]", "")),
            "geographic_connection": str(row.get("Why is this product special to this region? (Explain the connection between geography and product uniqueness)", ""))
        }
    
    def _extract_product_category(self, row) -> str:
        """Extract product category"""
        category_map = {
            "1": "Agricultural Products",
            "2": "Food & Beverages", 
            "3": "Handicrafts & Artisanal Products",
            "4": "Textiles & Fabrics",
            "5": "Natural Products & Extracts"
        }
        
        category_selection = str(row.get("Select Product Category", ""))
        return category_map.get(category_selection, "Unknown")
    
    def _extract_category_specific_data(self, row) -> Dict[str, Any]:
        """Extract category-specific data based on product category"""
        category = self._extract_product_category(row)
        
        if category == "Agricultural Products":
            return self._extract_agricultural_data(row)
        elif category == "Food & Beverages":
            return self._extract_food_beverage_data(row)
        elif category == "Handicrafts & Artisanal Products":
            return self._extract_handicraft_data(row)
        elif category == "Textiles & Fabrics":
            return self._extract_textile_data(row)
        elif category == "Natural Products & Extracts":
            return self._extract_natural_product_data(row)
        else:
            return {}
    
    def _extract_agricultural_data(self, row) -> Dict[str, str]:
        """Extract agricultural product specific data"""
        return {
            "crop_plant_type": str(row.get("Crop/Plant Type (Scientific name and variety of the plant/crop)", "")),
            "physical_characteristics": str(row.get("Physical Characteristics( Describe size, color, shape, texture of the agricultural product )", "")),
            "taste_aroma": str(row.get("Taste & Aroma Profile (Detailed description of taste, flavor, and aromatic properties)", "")),
            "nutritional_properties": str(row.get("Nutritional Properties (Nutritional content, vitamins, minerals, and health benefits)", "")),
            "harvest_season": str(row.get("Harvest Season [When is the product typically harvested? (months/seasons)]", "")),
            "soil_requirements": str(row.get("Soil Requirements (Specific soil type, pH, and conditions needed for cultivation)", "")),
            "climate_requirements": str(row.get("Climate Requirements ( Temperature, rainfall, humidity requirements for optimal growth )", "")),
            "traditional_methods": str(row.get("Traditional Growing Methods (Traditional cultivation practices passed down through generations)", "")),
            "seeds_planting": str(row.get("Seeds/Planting Material (Source and characteristics of traditional seeds or planting material used)", "")),
            "pest_control": str(row.get("Natural Pest Control (Traditional methods of pest and disease management)", "")),
            "post_harvest": str(row.get("Post-Harvest Processing [Steps taken immediately after harvest (drying, cleaning, sorting)]", "")),
            "storage_methods": str(row.get("Traditional Storage Methods ( How the product is traditionally stored and preserved)", "")),
            "quality_grading": str(row.get("Quality Grading (Traditional methods of quality assessment and grading)", "")),
            "average_yield": str(row.get("Average Yield per Acre (Typical production quantity per unit area)", "")),
            "total_production": str(row.get("Total Annual Production (Total quantity produced annually in the region)", "")),
            "number_farmers": str(row.get("Number of Farmers Involved (Approximate number of farmers/producers in the region)", "")),
            "price_premium": str(row.get("Price Premium ( How much more does this product sell for compared to similar products from other regions?)", "")),
            "export_markets": str(row.get("Export Markets (Countries/regions where this product is exported)", "")),
            "farmer_income": str(row.get("Farmer Income Impact (How has this product improved farmer incomes and livelihoods?)", ""))
        }
    
    def _extract_food_beverage_data(self, row) -> Dict[str, str]:
        """Extract food and beverage specific data"""
        return {
            "food_category": str(row.get("Food Category", "")),
            "main_ingredients": str(row.get("Main Ingredients (List all primary ingredients and their sources)", "")),
            "taste_profile": str(row.get("Taste Profile (Detailed description of taste, texture, and sensory characteristics)", "")),
            "nutritional_benefits": str(row.get("Nutritional Benefits (Health benefits, nutritional content, medicinal properties if any)", "")),
            "shelf_life": str(row.get("Shelf Life ( How long does the product stay fresh under normal conditions?)", "")),
            "traditional_recipe": str(row.get("Traditional Recipe ( Detailed traditional recipe or preparation method )", "")),
            "special_techniques": str(row.get("Secret/Special Techniques (Any unique techniques or secrets that make this product special)", "")),
            "traditional_equipment": str(row.get("Traditional Equipment ( Special equipment, utensils, or tools used in preparation)", "")),
            "aging_process": str(row.get("Aging/Fermentation Process (If applicable, describe aging, fermentation, or curing processes)", "")),
            "quality_control": str(row.get("Quality Control in Preparation ( How is quality maintained during preparation?)", "")),
            "local_materials": str(row.get("Local Raw Materials (Which ingredients must come from the specific geographical region?)", "")),
            "seasonal_availability": str(row.get("Seasonal Availability (How does seasonality affect availability of ingredients and production?)", "")),
            "traditional_suppliers": str(row.get("Traditional Suppliers (Who are the traditional suppliers of raw materials?)", "")),
            "festival_use": str(row.get("Festival/Ceremonial Use (Is this food associated with specific festivals, ceremonies, or cultural events?)", "")),
            "consumption_patterns": str(row.get("Traditional Consumption Patterns  (How and when is this food traditionally consumed?)", "")),
            "cultural_stories": str(row.get("Cultural Stories/Legends (Any cultural stories, legends, or folklore associated with this food)", "")),
            "daily_production": str(row.get("Daily/Monthly Production  (Typical production quantities per day or month)", "")),
            "number_producers": str(row.get("Number of Traditional Producers (How many families/businesses are involved in traditional production?)", "")),
            "market_reach": str(row.get("Market Reach (Local, regional, national, or international market presence)", ""))
        }
    
    def _extract_handicraft_data(self, row) -> Dict[str, str]:
        """Extract handicraft specific data"""
        return {
            "craft_type": str(row.get("Type of Handicraft", "")),
            "dimensions": str(row.get("Product Dimensions (Typical size and dimensions of the finished product)", "")),
            "materials": str(row.get("Materials Used  (All raw materials used and their local sources)", "")),
            "design_features": str(row.get("Distinctive Design Features (What makes the design unique to this region?)", "")),
            "functional_use": str(row.get("Functional Use ( How is this product used in daily life or special occasions?)", "")),
            "manufacturing_process": str(row.get("Manufacturing Process (Step-by-step description of the traditional making process)", "")),
            "special_tools": str(row.get("Special Tools & Equipment (Traditional tools and equipment used by artisans)", "")),
            "skill_requirements": str(row.get("Skill Requirements (What specific skills and training do artisans need?)", "")),
            "time_to_create": str(row.get("Time to Create (How long does it take to create one piece?)", "")),
            "design_patterns": str(row.get("Design Patterns/Motifs (Traditional patterns, motifs, or designs that are characteristic of the region)", "")),
            "number_artisans": str(row.get("Number of Active Artisans (How many artisans are currently practicing this craft?)", "")),
            "community_background": str(row.get("Community Background ( Which communities/families have traditionally practiced this craft?)", "")),
            "skill_transfer": str(row.get("Skill Transfer Method (How are skills passed down to new generations?)", "")),
            "training_period": str(row.get("Training Period (How long does it take to train a new artisan?)", "")),
            "historical_significance": str(row.get("Historical Significance (Historical importance and cultural significance of this craft)", "")),
            "traditional_uses": str(row.get("Traditional Uses in Society  (How was/is this product used in traditional society?)", "")),
            "symbolic_meaning": str(row.get("Symbolic Meaning (Any symbolic or spiritual significance of the craft)", "")),
            "production_capacity": str(row.get("Production Capacity (How many pieces can an artisan produce per month?)", "")),
            "price_range": str(row.get("Price Range  (Typical price range for different sizes/types)", "")),
            "market_challenges": str(row.get("Market Challenges ( What challenges do artisans face in marketing their products?)", ""))
        }
    
    def _extract_textile_data(self, row) -> Dict[str, str]:
        """Extract textile specific data"""
        return {
            "textile_type": str(row.get("Type of Textile*", "")),
            "fiber_type": str(row.get("Fiber Type (Thread count, weight, dimensions, thickness specifications)", "")),
            "color_palette": str(row.get("Color Palette (Traditional colors used and sources of natural dyes)", "")),
            "pattern_characteristics": str(row.get("Pattern/Design Characteristics (Distinctive patterns, motifs, or design elements)", "")),
            "loom_type": str(row.get("Traditional Loom Type ( Type of loom used and its characteristics)", "")),
            "weaving_technique": str(row.get("Weaving Technique ( Specific weaving techniques and methods used)", "")),
            "thread_preparation": str(row.get("Thread Preparation (How are threads prepared, spun, and treated before weaving?)", "")),
            "dyeing_process": str(row.get("Dyeing Process (Traditional dyeing methods and natural dye sources)", "")),
            "time_to_complete": str(row.get("Time to Complete ( How long does it take to complete one piece?)", "")),
            "weaver_community": str(row.get("Weaver Community ( Which communities have traditionally practiced this weaving?)", "")),
            "number_weavers": str(row.get("Number of Active Weavers (Current number of practicing weavers)", "")),
            "skill_complexity": str(row.get("Skill Complexity (Level of skill required and training needed)", "")),
            "design_creation": str(row.get("Design Creation Process (How are traditional designs created and modified?)", "")),
            "traditional_uses": str(row.get("Traditional Uses (How is this textile traditionally used in society?)", "")),
            "ceremonial_significance": str(row.get("Ceremonial Significance (Use in weddings, festivals, or religious ceremonies)", "")),
            "social_status": str(row.get("Social Status Indicators ( Does this textile indicate social status or community membership?)", "")),
            "production_per_weaver": str(row.get("Production per Weaver (Average monthly production per weaver)", "")),
            "raw_material_costs": str(row.get("Raw Material Costs ( Cost and availability of raw materials)", "")),
            "market_demand": str(row.get("Market Demand ( Current market demand and customer base)", ""))
        }
    
    def _extract_natural_product_data(self, row) -> Dict[str, str]:
        """Extract natural product specific data"""
        return {
            "product_type": str(row.get("Product Type", "")),
            "source_plant": str(row.get("Source Plant/Material (Scientific name and description of source plant or natural material)", "")),
            "active_compounds": str(row.get("Active Compounds (Key chemical compounds or active ingredients)", "")),
            "physical_properties": str(row.get("Physical Properties (Color, consistency, aroma, and physical characteristics)", "")),
            "traditional_uses": str(row.get("Traditional Uses (How has this product been traditionally used?)", "")),
            "collection_season": str(row.get("Collection Season [ When is the raw material collected? (months/seasons)]", "")),
            "collection_methods": str(row.get("Collection Methods  (Traditional methods of collection or harvesting)", "")),
            "processing_technique": str(row.get("Processing Technique (How is the final product extracted or processed?)", "")),
            "traditional_equipment": str(row.get("Traditional Equipment (Tools and equipment used in traditional processing)", "")),
            "quality_assessment": str(row.get("Quality Assessment (How is quality determined and maintained?)", "")),
            "habitat_requirements": str(row.get("Habitat Requirements (Specific environmental conditions needed for the source material)", "")),
            "sustainable_practices": str(row.get("Sustainable Practices (Traditional conservation and sustainability practices)", "")),
            "seasonal_variations": str(row.get("Seasonal Variations ( How do seasonal changes affect product quality?)", "")),
            "geographic_specificity": str(row.get("Geographic Specificity (Why can this product only be obtained from this specific region?)", "")),
            "indigenous_knowledge": str(row.get("Indigenous Knowledge (Traditional knowledge systems associated with this product)", "")),
            "community_guardians": str(row.get("Community Guardians ( Which communities have traditionally been guardians of this knowledge?)", "")),
            "traditional_applications": str(row.get("Traditional Applications (Detailed traditional uses in medicine, cosmetics, or daily life)", "")),
            "yield_per_collection": str(row.get("Yield per Collection ( Typical quantity obtained per collection/processing cycle)", "")),
            "market_applications": str(row.get("Market Applications ( Modern commercial applications and uses)", "")),
            "value_addition": str(row.get("Value Addition Potential (Opportunities for processing into higher-value products)", ""))
        }
    
    def _extract_historical_evidence(self, row) -> Dict[str, str]:
        """Extract historical evidence data"""
        return {
            "production_history": str(row.get("Production History (How long has this product been made in this region?)", "")),
            "historical_documents": str(row.get("Historical Documents (Any historical references, documents, or evidence)", "")),
            "cultural_evolution": str(row.get("Cultural Evolution  (How has production evolved while maintaining traditional character?)", ""))
        }
    
    def _extract_economic_impact(self, row) -> Dict[str, str]:
        """Extract economic impact data"""
        return {
            "producer_income": str(row.get("Producer Income (Average annual income per producer from this product )", "")),
            "employment_generation": str(row.get("Employment Generation (Number of people employed directly and indirectly)", "")),
            "regional_impact": str(row.get("Regional Economic Impact (Overall economic contribution to the region)", "")),
            "current_challenges": str(row.get("Current Challenges (Main challenges facing production and marketing)", "")),
            "growth_potential": str(row.get("Growth Potential (Potential for expanding production and markets)", "")),
            "support_needed": str(row.get("Support Needed ( What support is needed for development?)", ""))
        }
    
    def _extract_supporting_documents(self, row) -> Dict[str, str]:
        """Extract supporting documents information"""
        return {
            "product_photos": str(row.get("Product Photos ( High-quality photos of the product)", "")),
            "process_photos": str(row.get("Production Process Photos (Photos showing production/making process)", "")),
            "supporting_docs": str(row.get("Supporting Documents (Any certificates, awards, research papers, or other evidence)", "")),
            "unique_id": str(row.get("Unique Application ID [Enter a unique identifier for your application (used for file naming)]", ""))
        }
    
    def get_processed_data(self) -> Dict[str, Any]:
        """Get processed data"""
        return self.processed_data
    
    def validate_data_completeness(self) -> tuple[bool, List[str]]:
        """Validate that all required data is present"""
        if not self.processed_data:
            return False, ["No data has been processed yet"]
        
        missing_fields = []
        
        # Check required fields
        required_sections = ["applicant_info", "product_info", "geographic_info"]
        for section in required_sections:
            if section not in self.processed_data:
                missing_fields.append(f"Missing section: {section}")
        
        # Check critical fields
        if self.processed_data.get("product_info", {}).get("product_name", "").strip() == "":
            missing_fields.append("Product name is required")
        
        if self.processed_data.get("geographic_info", {}).get("region_of_origin", "").strip() == "":
            missing_fields.append("Region of origin is required")
        
        return len(missing_fields) == 0, missing_fields 