# GI Paper Writing Tool - Web Interface

A simple, elegant web interface for the GI Paper Writing Tool, built with HTML, CSS, and JavaScript.

## Features

- 📊 **Excel/Google Sheets Upload**: Upload and preview Excel files
- ✅ **Row Selection**: Select specific rows for paper generation
- 📅 **Date Selection**: Choose the date for paper generation
- 👤 **Signature Selection**: Select the author signature
- 📄 **Paper Generation**: Generate GI papers for selected data
- 📈 **Status Tracking**: Real-time status updates for paper generation

## Quick Start

### Option 1: Simple HTML (No Backend)
1. Open `index.html` directly in your browser
2. Upload an Excel file
3. Select rows and generate papers (simulated)

### Option 2: With Backend Integration
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python start_server.py
   ```

3. Open your browser and go to: `http://localhost:5000`

## File Structure

```
ui/
├── index.html          # Main HTML interface
├── server.py           # Flask backend server
├── start_server.py     # Startup script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Usage

1. **Upload Data**: Click "Choose File" and select your Excel/Google Sheets file
2. **Preview Data**: View your data in the preview table
3. **Select Rows**: Use checkboxes to select which rows to process
4. **Set Date**: Choose the date for paper generation
5. **Generate Papers**: Click "Generate GI Paper" to create papers for selected rows

## Data Format

The tool expects Excel files with the following columns:
- Column 1: GI Name
- Column 2: GI Description
- Column 3: GI Location
- Additional columns: Any other relevant data

## Customization

- **Theme**: Modify the CSS variables in the `[data-theme=gi]` section
- **Backend**: Update `server.py` to integrate with your specific paper generation logic
- **Styling**: Edit the embedded CSS in `index.html`

## Troubleshooting

- **Port already in use**: Change the port in `server.py` (line with `app.run()`)
- **Module import errors**: Ensure all Python modules are in the correct path
- **File upload issues**: Check that your Excel file is not corrupted

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## License

This interface is part of the GI Paper Writing Tool project. 