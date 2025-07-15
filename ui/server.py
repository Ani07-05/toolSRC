import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime
import pandas as pd
from modules.pdf_generator import generate_enhanced_paper_pdf
from modules.data_processor import GoogleFormProcessor, DataProcessor
from modules.academic_generator import AcademicGenerator
import re

# Add parent directory to path to import modules
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
CORS(app)

# Initialize modules lazily (only when needed)
data_processor = None
academic_generator = None
pdf_generator = None

def get_modules():
    """Lazy load modules only when needed"""
    global data_processor, academic_generator, pdf_generator
    
    if data_processor is None:
        try:
            from modules.data_processor import DataProcessor
            data_processor = DataProcessor()
        except ImportError as e:
            print(f"Warning: Could not import DataProcessor: {e}")
            data_processor = None
    
    if academic_generator is None:
        try:
            from modules.academic_generator import AcademicGenerator
            academic_generator = AcademicGenerator()
        except ImportError as e:
            print(f"Warning: Could not import AcademicGenerator: {e}")
            academic_generator = None
    
    if pdf_generator is None:
        try:
            # Import the function instead of a class
            from modules.pdf_generator import generate_paper_pdf
            pdf_generator = generate_paper_pdf
        except ImportError as e:
            print(f"Warning: Could not import PDF generator: {e}")
            pdf_generator = None
    
    return data_processor, academic_generator, pdf_generator

@app.route('/')
def index():
    return render_template('index.html')

import os
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/api/generate-paper-from-sheets', methods=['POST'])
def generate_paper_from_sheets():
    """Generate paper directly from Google Sheets URL"""
    try:
        data = request.json
        sheets_url = data.get('sheetsUrl', '')
        signature = data.get('signature', 'GI Research Team')
        
        if not sheets_url:
            return jsonify({'error': 'No Google Sheets URL provided'}), 400
        
        # Extract spreadsheet ID from URL
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
        if not match:
            return jsonify({'error': 'Invalid Google Sheets URL format'}), 400
        
        spreadsheet_id = match.group(1)
        
        try:
            # Initialize data processor
            data_processor = DataProcessor()
            
            # Process Google Sheets data
            processed_data = data_processor.process_google_sheets_data(spreadsheet_id)
            
            # Extract structured section data
            sections_data = data_processor.extract_paper_sections_data(processed_data)
            
            # Get the latest response for metadata
            latest_response = processed_data['latest_response']
            
            # Extract paper metadata
            product_name = latest_response.get(' Product Name ( Exact name you want to register for GI protection)', 'Untitled GI Product')
            applicant_name = latest_response.get('Applicant/Orginization Name', signature)
            institution = latest_response.get('Applicant/Orginization Name', 'Geographical Indication Research Team')
            category = latest_response.get('Select Product Category \n\nChoose the category that best describes your product', '')
            region = latest_response.get(' Region of Origin', '')
            
            # Generate title with product name and region
            title = f"Geographical Indication Protection for {product_name}"
            if region:
                title += f" from {region}"
            
            # Extract keywords from various fields
            keywords = []
            if product_name:
                keywords.append(product_name)
            if category:
                keywords.append(category)
            if region:
                keywords.append(region)
            
            # Add category-specific keywords
            if 'Agricultural' in category:
                crop_type = latest_response.get('Crop/Plant Type (Scientific name and variety of the plant/crop)', '')
                if crop_type:
                    keywords.append(crop_type)
            elif 'Handicraft' in category:
                craft_type = latest_response.get('Type of Handicraft', '')
                if craft_type:
                    keywords.append(craft_type)
            
            # Generate the academic paper using AI
            academic_gen = AcademicGenerator()
            paper = academic_gen.generate_full_paper(sections_data)
            
            # Generate filename
            safe_name = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'GI_Paper_{safe_name}_{timestamp}.pdf'
            pdf_path = os.path.join(OUTPUT_DIR, filename)
            
            # Generate enhanced PDF with all features
            generate_enhanced_paper_pdf(
                paper=paper,
                output_path=pdf_path,
                title=title,
                author=applicant_name,
                institution=institution,
                keywords=keywords[:5],  # Limit to 5 keywords
                include_toc=True
            )
            
            download_url = f'/api/download-paper/{filename}'
            
            result = {
                'status': 'success',
                'message': f'Paper generated successfully for {product_name}',
                'filename': filename,
                'download_url': download_url,
                'metadata': {
                    'title': title,
                    'author': applicant_name,
                    'institution': institution,
                    'category': category,
                    'region': region,
                    'total_responses_analyzed': processed_data['total_responses']
                },
                'sheets_url': sheets_url,
                'spreadsheet_id': spreadsheet_id
            }
            
            return jsonify(result)
            
        except PermissionError as e:
            return jsonify({
                'error': 'Permission denied. Please share the Google Sheet with the service account email.',
                'details': str(e),
                'solution': 'Check the server logs for the service account email address to share with.'
            }), 403
        except Exception as e:
            return jsonify({
                'error': f'Failed to process Google Sheets data: {str(e)}',
                'details': str(e)
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-paper', methods=['POST'])
def generate_paper():
    try:
        data = request.json or {}
        sheets_url = data.get('sheetsUrl', '').strip()
        row_data = data.get('rowData', [])
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        signature = data.get('signature', 'GI Research Team')

        # ------------------------------------------------------------------
        # 1️⃣  GOOGLE SHEETS MODE (takes priority if sheetsUrl provided)
        # ------------------------------------------------------------------
        if sheets_url:
            # Validate URL and extract spreadsheet ID
            match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
            if not match:
                return jsonify({'error': 'Invalid Google Sheets URL format'}), 400

            spreadsheet_id = match.group(1)

            try:
                data_processor = DataProcessor()
                processed_data = data_processor.process_google_sheets_data(spreadsheet_id)
                sections_data = data_processor.extract_paper_sections_data(processed_data)

                latest_response = processed_data['latest_response']

                # Extract metadata
                product_name = latest_response.get(' Product Name ( Exact name you want to register for GI protection)', 'Untitled GI Product')
                applicant_name = latest_response.get('Applicant/Orginization Name', 'GI Research Team')
                institution = applicant_name or 'Geographical Indication Research Team'
                category = latest_response.get('Select Product Category \n\nChoose the category that best describes your product', '')
                region = latest_response.get(' Region of Origin', '')

                # Build title
                title = f"Geographical Indication Protection for {product_name}"
                if region:
                    title += f" from {region}"

                # Keywords
                keywords = list(filter(None, {product_name, category, region}))

                academic_gen = AcademicGenerator()
                paper = academic_gen.generate_full_paper(sections_data)

                # Generate PDF
                safe_name = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'GI_Paper_{safe_name}_{timestamp}.pdf'
                pdf_path = os.path.join(OUTPUT_DIR, filename)

                generate_enhanced_paper_pdf(
                    paper=paper,
                    output_path=pdf_path,
                    title=title,
                    author=applicant_name,
                    institution=institution,
                    keywords=keywords[:5],
                    include_toc=True
                )

                download_url = f'/api/download-paper/{filename}'

                return jsonify({
                    'status': 'success',
                    'message': f'Paper generated successfully for {product_name}',
                    'filename': filename,
                    'download_url': download_url,
                    'metadata': {
                        'title': title,
                        'author': applicant_name,
                        'institution': institution,
                        'category': category,
                        'region': region,
                        'total_responses_analyzed': processed_data['total_responses']
                    },
                    'method': 'google_sheets'
                })

            except PermissionError as e:
                return jsonify({'error': str(e), 'tip': 'Share the sheet with the service account email'}), 403
            except Exception as e:
                return jsonify({'error': f'Failed to process Google Sheets data: {str(e)}'}), 500

        # ------------------------------------------------------------------
        # 2️⃣  MANUAL / FILE UPLOAD MODE (legacy)
        # ------------------------------------------------------------------
        if not row_data:
            return jsonify({'error': 'No data provided. Provide rowData or sheetsUrl.'}), 400

        try:
            headers = data.get('headers')
            
            # If no headers provided, use common fallback field names
            if not headers:
                # Based on the actual Google Form structure from debug output
                # The real data positions are:
                # 0: Timestamp, 1: Email, 2: Applicant Name, 3: Applicant Type, 4: Email again, 5: Phone
                # 6: Address, 7: PRODUCT NAME, 8: empty, 9: Common/Local Names, 10: REGION, 11: State
                # 12: Geographic boundaries, 13: Geographic connection, 14: CATEGORY
                
                # Create a mapping that puts the real data in the right places
                response_dict = {}
                
                if len(row_data) > 7:
                    response_dict[' Product Name ( Exact name you want to register for GI protection)'] = row_data[7]  # Blue Pottery of Jaipur
                if len(row_data) > 10:
                    response_dict[' Region of Origin'] = row_data[10]  # Jaipur Region
                if len(row_data) > 11:
                    response_dict['State/Province (Primary state or province of production)'] = row_data[11]  # Rajasthan
                if len(row_data) > 14:
                    response_dict['Select Product Category \n\nChoose the category that best describes your product'] = row_data[14]  # Handicrafts & Artisanal Products
                if len(row_data) > 2:
                    response_dict['Applicant/Orginization Name'] = row_data[2]  # Satyam Goyal
                if len(row_data) > 9:
                    response_dict['Common/Local Names (All alternative names by which this product is known locally)'] = row_data[9]  # Neela Bartan, Jaipur Blue Ceramics
                if len(row_data) > 12:
                    response_dict['Specific Geographic Boundaries [Exact boundaries of the geographical area (villages, taluks, coordinates if available)]'] = row_data[12]
                if len(row_data) > 13:
                    response_dict['Why is this product special to this region? (Explain the connection between geography and product uniqueness)'] = row_data[13]
                
                # Add more fields based on the debug output showing all the data
                # The form has many more fields that we can map
                field_positions = {
                    16: 'Type of Handicraft',
                    17: 'Product Dimensions (Typical size and dimensions of the finished product)',
                    18: 'Materials Used  (All raw materials used and their local sources)',
                    19: 'Distinctive Design Features (What makes the design unique to this region?)',
                    20: 'Functional Use ( How is this product used in daily life or special occasions?)',
                    21: 'Manufacturing Process (Step-by-step description of the traditional making process)',
                    22: 'Special Tools & Equipment (Traditional tools and equipment used by artisans)',
                    23: 'Skill Requirements (What specific skills and training do artisans need?)',
                    24: 'Time to Create (How long does it take to create one piece?)',
                    25: 'Design Patterns/Motifs (Traditional patterns, motifs, or designs that are characteristic of the region)',
                    26: 'Number of Active Artisans (How many artisans are currently practicing this craft?)',
                    27: 'Community Background ( Which communities/families have traditionally practiced this craft?)',
                    28: 'Skill Transfer Method (How are skills passed down to new generations?)',
                    29: 'Training Period (How long does it take to train a new artisan?)',
                    30: 'Historical Significance (Historical importance and cultural significance of this craft)',
                    31: 'Traditional Uses in Society  (How was/is this product used in traditional society?)',
                    32: 'Symbolic Meaning (Any symbolic or spiritual significance of the craft)',
                    33: 'Production Capacity (How many pieces can an artisan produce per month?)',
                    34: 'Price Range  (Typical price range for different sizes/types)',
                    35: 'Market Challenges ( What challenges do artisans face in marketing their products?)',
                    70: 'Production History (How long has this product been made in this region?)',
                    71: 'Historical Documents (Any historical references, documents, or evidence)',
                    72: 'Cultural Evolution  (How has production evolved while maintaining traditional character?)',
                    73: 'Producer Income (Average annual income per producer from this product )',
                    74: 'Employment Generation (Number of people employed directly and indirectly)',
                    75: 'Regional Economic Impact (Overall economic contribution to the region)',
                    76: 'Current Challenges (Main challenges facing production and marketing)',
                    77: 'Growth Potential (Potential for expanding production and markets)',
                    78: 'Support Needed ( What support is needed for development?)'
                }
                
                for pos, field_name in field_positions.items():
                    if len(row_data) > pos and row_data[pos]:
                        response_dict[field_name] = row_data[pos]
                        
            else:
                # Build response dict from row_data and headers
                response_dict = {header: val for header, val in zip(headers, row_data) if val}
            
            print(f"🔍 DEBUG - Final Response Dict Keys: {list(response_dict.keys())}")
            print(f"🔍 DEBUG - Product Name: {response_dict.get(' Product Name ( Exact name you want to register for GI protection)', 'NOT FOUND')}")
            print(f"🔍 DEBUG - Region: {response_dict.get(' Region of Origin', 'NOT FOUND')}")

            processed_data = {
                'latest_response': response_dict,
                'total_responses': 1
            }

            data_processor = DataProcessor()
            sections_data = data_processor.extract_paper_sections_data(processed_data)
            
            print(f"🔍 DEBUG - Sections Data Keys: {list(sections_data.keys())}")
            for section, data in sections_data.items():
                non_empty_fields = {k: v for k, v in data.items() if v}
                print(f"🔍 DEBUG - {section}: {len(non_empty_fields)} non-empty fields")
                if non_empty_fields:
                    print(f"   Sample fields: {list(non_empty_fields.keys())[:3]}")

            product_name = response_dict.get(' Product Name ( Exact name you want to register for GI protection)', 'Untitled GI Product')
            region = response_dict.get(' Region of Origin', '')

            title = f"Geographical Indication Protection for {product_name}"
            if region:
                title += f" from {region}"

            keywords = [k for k in (product_name, region) if k]

            try:
                academic_gen = AcademicGenerator()
                print(f"🔍 DEBUG - Sending to AI: {product_name} from {region}")
                paper = academic_gen.generate_full_paper(sections_data)
                print(f"🔍 DEBUG - AI Generated paper with sections: {list(paper.keys())}")
            except Exception as e:
                print(f"❌ AI Generation Failed: {str(e)}")
                paper = {
                    'abstract': f"This paper presents the case for Geographical Indication protection for {product_name} from {region}.",
                    'introduction': f"The {product_name} from {region} represents a unique product with distinct characteristics.",
                    'literature_review': "Literature review section pending detailed analysis.",
                    'methodology': "Methodology section requires comprehensive data collection.",
                    'results': "Results section will be populated with empirical data.",
                    'conclusion': f"The {product_name} merits GI protection based on its unique regional characteristics."
                }

            safe_name = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')
            filename = f'GI_Paper_{safe_name}_{date}.pdf'
            pdf_path = os.path.join(OUTPUT_DIR, filename)

            generate_enhanced_paper_pdf(
                paper=paper,
                output_path=pdf_path,
                title=title,
                author=signature,
                institution="Geographical Indication Research Team",
                keywords=keywords[:5],
                include_toc=True
            )

            download_url = f'/api/download-paper/{filename}'

            return jsonify({
                'status': 'success',
                'message': f'Paper generation successfully for {product_name}',
                'filename': filename,
                'download_url': download_url,
                'metadata': {
                    'title': title,
                    'author': signature,
                    'product_name': product_name,
                    'region': region
                },
                'method': 'manual_entry'
            })

        except Exception as e:
            return jsonify({'error': f'Paper generation failed: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch-sheet-responses', methods=['POST'])
def fetch_sheet_responses():
    """Return all responses from a Google Form responses sheet as rows (including header)."""
    try:
        data = request.json or {}
        sheets_url = data.get('sheetsUrl', '').strip()
        if not sheets_url:
            return jsonify({'error': 'No sheetsUrl provided'}), 400

        # Extract spreadsheet ID
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
        if not match:
            return jsonify({'error': 'Invalid Google Sheets URL format'}), 400
        spreadsheet_id = match.group(1)

        # Use GoogleSheetsProcessor to fetch raw values
        dp = DataProcessor()
        df = dp.sheets_processor.get_form_responses(spreadsheet_id)
        # Convert DataFrame to list of rows (include header)
        rows = [df.columns.tolist()] + df.values.tolist()
        return jsonify({'status': 'success', 'rows': rows, 'total': len(df), 'spreadsheet_id': spreadsheet_id})
    except PermissionError as e:
        return jsonify({'error': str(e), 'tip': 'Share the sheet with the service account email'}), 403
    except Exception as e:
        return jsonify({'error': f'Failed to fetch sheet responses: {str(e)}'}), 500

@app.route('/api/download-paper/<filename>', methods=['GET'])
def download_paper(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'modules_available': all(get_modules())
    })

@app.route('/api/modules-status', methods=['GET'])
def modules_status():
    """Check which modules are available"""
    data_proc, acad_gen, pdf_gen = get_modules()
    return jsonify({
        'data_processor': data_proc is not None,
        'academic_generator': acad_gen is not None,
        'pdf_generator': pdf_gen is not None,
        'all_available': all([data_proc, acad_gen, pdf_gen])
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Copy index.html to templates directory
    import shutil
    src_file = os.path.join(os.path.dirname(__file__), 'index.html')
    dst_file = os.path.join(templates_dir, 'index.html')
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
    
    print("Starting GI Paper Writing Tool server...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 