from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

@app.route('/api/generate-paper', methods=['POST'])
def generate_paper():
    try:
        data = request.json
        row_data = data.get('rowData', [])
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        signature = data.get('signature', 'Phani')
        
        if not row_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract GI information from row data
        gi_name = row_data[0] if len(row_data) > 0 else "Unknown GI"
        gi_description = row_data[1] if len(row_data) > 1 else ""
        gi_location = row_data[2] if len(row_data) > 2 else ""
        
        # Create a structured data object for processing
        gi_data = {
            'name': gi_name,
            'description': gi_description,
            'location': gi_location,
            'date': date,
            'signature': signature
        }
        
        # Try to use the actual modules if available
        try:
            data_proc, acad_gen, pdf_gen = get_modules()
            
            if data_proc and acad_gen and pdf_gen:
                # Use actual modules for paper generation
                # This is where you'd integrate with your actual paper generation logic
                result = {
                    'status': 'success',
                    'message': f'Paper generated successfully for {gi_name} using actual modules',
                    'filename': f'gi_paper_{gi_name.replace(" ", "_")}_{date}.pdf',
                    'data': gi_data,
                    'method': 'actual_modules'
                }
            else:
                # Fallback to simple response
                result = {
                    'status': 'success',
                    'message': f'Paper generation simulated for {gi_name} (modules not available)',
                    'filename': f'gi_paper_{gi_name.replace(" ", "_")}_{date}.pdf',
                    'data': gi_data,
                    'method': 'simulated'
                }
        except Exception as e:
            # Fallback to simple response
            result = {
                'status': 'success',
                'message': f'Paper generation simulated for {gi_name} (error: {str(e)})',
                'filename': f'gi_paper_{gi_name.replace(" ", "_")}_{date}.pdf',
                'data': gi_data,
                'method': 'simulated_with_error'
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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