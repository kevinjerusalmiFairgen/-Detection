#!/usr/bin/env python3
"""Shared utilities for the Detection Pipeline"""

import os
import sys

def get_api_key():
    """
    Get Gemini API key from multiple sources in order of priority:
    1. Streamlit secrets (for Streamlit Cloud)
    2. Environment variable (for server deployment)
    3. Local api_keys.py file (for local development)
    
    Returns:
        str: The API key
        
    Raises:
        ValueError: If no API key is found
    """
    # Try Streamlit secrets first
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except:
        pass
    
    # Try environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # Try local api_keys file
    try:
        from api_keys import GEMINI_API_KEY
        return GEMINI_API_KEY
    except ImportError:
        pass
    
    raise ValueError(
        "GEMINI_API_KEY not found. Please set it in:\n"
        "1. Streamlit secrets (for cloud deployment)\n"
        "2. Environment variable GEMINI_API_KEY\n"
        "3. Local api_keys.py file"
    )

def progress_print(message, level="info", verbose=True):
    """
    Print progress messages with consistent formatting.
    
    Args:
        message: The message to print
        level: "info", "success", "warning", "error"
        verbose: If False, suppress info messages
    """
    if not verbose and level == "info":
        return
        
    symbols = {
        "info": "→",
        "success": "✓",
        "warning": "⚠",
        "error": "✗"
    }
    
    symbol = symbols.get(level, "→")
    print(f"{symbol} {message}")