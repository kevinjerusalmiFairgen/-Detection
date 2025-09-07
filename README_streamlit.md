# 🔍 Detection Pipeline - Streamlit App

Web interface for the multiselect groups detection pipeline.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up API Key
Create `api_keys.py` with your Gemini API key:
```python
GEMINI_API_KEY = "your_gemini_api_key_here"
```

### 3. Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 How to Use

1. **Upload Files**:
   - Data file (.sav, .xlsx, .csv)
   - Questionnaire PDF (.pdf)

2. **Run Pipeline**:
   - Click "🚀 Run Pipeline"
   - Watch progress in real-time

3. **Download Results**:
   - Download complete ZIP with all files
   - Download individual JSON files
   - View debug information

## 📊 Features

- ✅ **Drag & Drop Upload** - Easy file upload interface
- ✅ **Real-time Progress** - See pipeline progress live
- ✅ **Complete Results** - Groups + recodes detection
- ✅ **Debug Information** - Full logs for each step
- ✅ **Downloadable ZIP** - All results in one package
- ✅ **Results Preview** - See sample groups in the UI

## 📁 Output Files

The app generates:
- `final_structure.json` - Main results with groups and recodes
- `step1_metadata.json` - Data variables metadata
- `step2_questionnaire_metadata.json` - PDF analysis results
- `debug_info.json` - Pipeline execution details
- `*_log.txt` - Individual step logs

## 🔧 Supported Formats

**Data Files:**
- SPSS (.sav)
- Excel (.xlsx, .xls)
- CSV (.csv)

**Questionnaire:**
- PDF (.pdf)

## ⚡ Performance

Typical processing times:
- Small datasets (< 1000 vars): 2-5 minutes
- Medium datasets (1000-3000 vars): 5-10 minutes  
- Large datasets (3000+ vars): 10-15 minutes

## 🛠️ Troubleshooting

**Common Issues:**

1. **API Key Error**: Make sure `api_keys.py` exists with valid Gemini API key
2. **File Upload Error**: Check file formats are supported
3. **Processing Timeout**: Large files may take 10-15 minutes
4. **Memory Error**: Very large datasets may need more RAM

**Debug Information:**
- Use the "🔧 Debug Information" section to see detailed logs
- Download the ZIP file to get complete debug info
- Check individual step logs for specific errors

## 📞 Support

For issues or questions, check the debug logs first. The app provides comprehensive error information to help diagnose problems.
