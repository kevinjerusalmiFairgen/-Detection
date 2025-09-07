# 🚀 Deployment Instructions - Streamlit Cloud

## 📋 Steps to Deploy

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Streamlit app"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `kevinjerusalmiFairgen/-Detection`
4. Set main file: `app.py`
5. Click "Deploy"

### 3. Add API Key Secret

**CRITICAL**: Add your Gemini API key in Streamlit Cloud:

1. In your deployed app, click "⚙️ Settings"
2. Go to "Secrets" tab
3. Add this content:

```toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

4. Click "Save"
5. App will restart automatically

## 🔧 Troubleshooting

### Common Issues:

**1. "api_keys not found"**
- ✅ Add API key in Streamlit Cloud secrets (step 3 above)

**2. "Module not found"**
- ✅ Check `requirements.txt` includes all dependencies
- ✅ Make sure all Python files are in repo

**3. "File not found"**
- ✅ Check file paths are relative, not absolute
- ✅ Ensure all data files are in repo (or uploaded via UI)

**4. "Memory/timeout errors"**
- ✅ Large datasets may hit Streamlit Cloud limits
- ✅ Consider using smaller test files first

## 📁 Required Files in Repo

Make sure these files are pushed:
- ✅ `app.py` (main Streamlit app)
- ✅ `step1_extract_spss_metadata.py`
- ✅ `step2_extract_questionnaire_metadata.py` 
- ✅ `step3_create_final_structure.py`
- ✅ `requirements.txt`
- ✅ `config.py` (API key management)
- ❌ `api_keys.py` (keep in .gitignore for security)

## 🌐 Access Your App

After deployment:
- Your app will be available at: `https://your-app-name.streamlit.app`
- Share this URL with users
- App updates automatically when you push to GitHub

## 🔒 Security Notes

- ✅ Never commit `api_keys.py` to GitHub
- ✅ Use Streamlit Cloud secrets for API keys
- ✅ API keys are encrypted and secure in Streamlit Cloud
- ✅ Only you can see/edit the secrets
