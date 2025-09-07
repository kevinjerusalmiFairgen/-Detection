#!/usr/bin/env python3
"""
Configuration management for different deployment environments
"""

import os

def get_gemini_api_key():
    """Get Gemini API key from various sources"""
    
    # 1. Try local api_keys.py (development)
    try:
        from api_keys import GEMINI_API_KEY
        return GEMINI_API_KEY
    except ImportError:
        pass
    
    # 2. Try Streamlit secrets (Streamlit Cloud)
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except:
        pass
    
    # 3. Try environment variable (Docker/Heroku)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    
    # 4. Fallback error
    raise ValueError(
        "GEMINI_API_KEY not found. Please set it in:\n"
        "- api_keys.py (local development)\n"
        "- Streamlit secrets (cloud deployment)\n" 
        "- Environment variable GEMINI_API_KEY"
    )
