#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import pyreadstat
import pandas as pd
import numpy as np


def build_spss_questions(meta):
    """Extract questions from SPSS metadata."""
    questions = []
    column_names = list(meta.column_names or [])
    column_labels = list(meta.column_labels or [])
    
    # Get value labels
    variable_value_labels = getattr(meta, "variable_value_labels", {}) or {}
    value_labels_catalog = getattr(meta, "value_labels", {}) or {}
    variable_to_labelset = getattr(meta, "variable_to_labelset", {}) or {}
    
    for i, var_name in enumerate(column_names):
        # Get question text
        question_text = column_labels[i] if i < len(column_labels) and column_labels[i] else var_name
        
        # Get possible answers
        possible_answers = {}
        
        # Check for value labels
        if var_name in variable_value_labels and variable_value_labels[var_name]:
            value_labels = variable_value_labels[var_name]
        elif var_name in variable_to_labelset:
            labelset = variable_to_labelset[var_name]
            value_labels = value_labels_catalog.get(labelset, {})
        else:
            value_labels = {}
        
        if value_labels:
            # Check if all numeric and many values (>25) -> show range
            try:
                numeric_keys = [float(k) for k in value_labels.keys()]
                if len(numeric_keys) > 25:
                    possible_answers = {"min": min(numeric_keys), "max": max(numeric_keys)}
                else:
                    possible_answers = {str(k): v for k, v in value_labels.items()}
            except:
                # Not all numeric, keep as is
                possible_answers = {str(k): v for k, v in value_labels.items()}
        
        questions.append({
            "question_code": var_name,
            "question_text": question_text,
            "possible_answers": possible_answers
        })

    return questions


def filter_useless_columns(df, questions):
    """
    Filter columns not useful for analysis:
    - Empty (all NaN)
    - Single value (no variance)  
    - Identifiers (all unique)
    - High-cardinality text (>80% unique)
    - System columns (uuid, timestamp, etc.)
    """
    filtered = []
    code_to_question = {q['question_code']: q for q in questions}
    
    for col in df.columns:
        if str(col) not in code_to_question:
            continue
            
        question = code_to_question[str(col)]
        data = df[col].dropna()
        
        # Skip empty columns
        if len(data) == 0:
            continue
        
        # Skip single value columns
        unique_count = data.nunique()
        if unique_count == 1:
            continue
        
        # Skip likely identifiers (all unique)
        if unique_count == len(data) and len(data) > 10:
            continue
        
        # Skip high cardinality text
        try:
            pd.to_numeric(data)
        except:
            if unique_count / len(data) > 0.8 and len(data) > 20:
                continue
        
        # Skip system columns
        col_lower = str(col).lower()
        system_words = ['uuid', 'guid', '_id', 'timestamp', 'created', 'updated']
        if any(word in col_lower for word in system_words):
            continue
        
        filtered.append(question)
    
    return filtered


def build_csv_excel_questions(df):
    """Extract questions from CSV/Excel file."""
    questions = []
    
    for col in df.columns:
        col_str = str(col)
        data = df[col].dropna()
        possible_answers = {}
        
        if len(data) > 0:
            try:
                # Numeric column - show range
                numeric_data = pd.to_numeric(data)
                possible_answers = {
                    "min": float(numeric_data.min()),
                    "max": float(numeric_data.max())
                }
            except:
                # String column - show values or mark as freetext
                unique_vals = data.astype(str).unique()
                if len(unique_vals) > 25:
                    possible_answers = {"type": "freetext", "count": len(unique_vals)}
                else:
                    possible_answers = {val: val for val in sorted(unique_vals)}
        
        questions.append({
            "question_code": col_str,
            "question_text": col_str,
            "possible_answers": possible_answers
        })
    
    return questions


def main():
    parser = argparse.ArgumentParser(
        description="Extract metadata from SPSS, CSV, or Excel files to JSON."
    )
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    input_path = Path(args.input)
    suffix = input_path.suffix.lower()
    
    print(f"Reading {suffix} file: {args.input}")
    
    # Extract questions based on file type
    if suffix == '.sav':
        _, meta = pyreadstat.read_sav(args.input, metadataonly=True)
        questions = build_spss_questions(meta)
    elif suffix == '.csv':
        df = pd.read_csv(args.input)
        questions = build_csv_excel_questions(df)
    elif suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(args.input)
        questions = build_csv_excel_questions(df)
    else:
        raise SystemExit(f"Unsupported file type: {suffix}")
    
    print(f"Extracted {len(questions)} questions")
    
    # Save or print JSON
    output = json.dumps(questions, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()


