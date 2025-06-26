# 🚀 Quick Start Guide

## Option 1: Simple HTML (No Backend)
1. **Open** `index.html` directly in your browser
2. **Upload** an Excel file
3. **Select** rows and generate papers (simulated)

## Option 2: Full Backend Integration

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server
**Windows:**
```bash
start.bat
```
**Or manually:**
```bash
python start_server.py
```

### Step 3: Open in Browser
Go to: **http://localhost:5000**

## 🧪 Testing

### Generate Sample Data
```bash
python sample_data.py
```

### Test the Server
```bash
python test_ui.py
```

## 📁 Files Overview

- `index.html` - Main web interface
- `server.py` - Flask backend server
- `start_server.py` - Startup script
- `start.bat` - Windows batch file
- `sample_data.py` - Generate test data
- `test_ui.py` - Test the interface

## 🎯 What You Can Do

1. **Upload Excel/Google Sheets** files
2. **Preview data** in a table format
3. **Select specific rows** for processing
4. **Choose date and signature**
5. **Generate GI papers** for selected data
6. **Track generation status** in real-time

## 🔧 Troubleshooting

- **Port 5000 in use**: Change port in `server.py`
- **Module errors**: Check Python path and dependencies
- **File upload issues**: Ensure Excel file is not corrupted

## 📞 Support

Check the main `README.md` for detailed documentation. 