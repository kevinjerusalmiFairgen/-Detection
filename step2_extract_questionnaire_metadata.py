#!/usr/bin/env python3
"""
Step 2: Extract metadata from questionnaire PDFs using Gemini Flash
Focus: Identify multi-select questions and recode mappings (split analysis)
"""

import json
import sys
import time
from pathlib import Path
import google.generativeai as genai
from utils import get_api_key, progress_print

def find_multiselect_questions(uploaded_file):
    """Specialized analysis for multi-select questions only"""
    start_time = time.time()
    
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json"
    )
    
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction="You are an expert survey methodology detective with deep knowledge of questionnaire design. Focus ONLY on finding multi-select questions."
    )
    
    # File already uploaded, passed as parameter
    
    prompt = """
OBJECTIVE: Find ALL multi-select questions (questions where respondent can choose multiple options)

MULTI-SELECT DETECTION PATTERNS:
- Explicit text: "Select all that apply", "Check all", "Multiple answers", "Mark all"
- Grid layouts: Multiple columns with same response scale  
- Lists of items/brands/features where multiple can be selected
- Programming clues: Conditional logic, loops, arrays indicate multi-structure
- VARIABLE CODE PATTERNS: Question codes that suggest groupings (Q1_1, Q1_2, Q1_3 series)
- QUESTION TEXT ANALYSIS: Content that obviously represents grouped concepts

GROUPING STRATEGY:
PREFER SUBGROUPS over big general groups:
- Better: Separate brand categories, occasion types, demographic segments
- Worse: One massive group combining everything
- Identify natural subgroupings from questionnaire structure and content

INTELLIGENCE-BASED SEARCH STRATEGY:
1. Scan ENTIRE questionnaire for multi-select patterns
2. Look in headers, footers, programming sections, notes
3. Find implicit groups: Same question stem across pages
4. Use programming text as primary intelligence source

OUTPUT SCHEMA (JSON array only):
[
  {
    "question_code": "Q1",
    "question_text": "Which brands do you know?",
    "type": "multi", 
    "possible_answers": {"1": "Brand A", "2": "Brand B", "3": "Brand C"},
    "grouping_hint": "Short reason why this is a multi-select group pattern"
  }
]

CRITICAL SUCCESS FACTORS:
- Find ALL multi-select patterns (miss nothing!)
- BREAK DOWN into specific subgroups when possible
- Use programming text as primary intelligence source  
- Use variable code patterns and question text to identify obvious groupings
- Clean programming prefixes from possible_answers
- Return comprehensive results with meaningful subgroups
"""

    thinking_prompt = f"""
    Think deeply about multi-select question detection.
    Use your full reasoning capacity to find ALL multi-select patterns.
    
    {prompt}
    
    Analyze systematically for comprehensive multi-select detection.
    """
    
    response = model.generate_content([thinking_prompt, uploaded_file])
    # Don't delete here - will delete after both functions complete
    
    try:
        result = json.loads(response.text)
        if isinstance(result, dict) and 'variables' in result:
            result = result['variables']
        elif not isinstance(result, list):
            result = []
        progress_print(f"Multi-select: {len(result)} patterns found ({time.time() - start_time:.1f}s)", "success")
        return result
    except:
        progress_print(f"Multi-select analysis failed ({time.time() - start_time:.1f}s)", "error")
        return []

def find_recode_variables(uploaded_file):
    """Specialized analysis for recode variables only"""
    start_time = time.time()
    
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json"
    )
    
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction="You are an expert survey methodology detective specializing in recode detection. Focus ONLY on finding variable transformations and computed variables."
    )
    
    # File already uploaded, passed as parameter
    
    prompt = """
OBJECTIVE: Find ALL recode variables (survey responses transformed/grouped into new variables)

RECODE DETECTION PATTERNS:
- Detailed responses grouped into broader categories
- Numerical data converted to ranges/bands
- Multiple variables combined into indices
- Geographic data aggregated to regions
- HIDDEN LOGIC: Implicit classification rules (quota, segmentation, targeting)
- BUSINESS LOGIC: Survey ops create classifications like buyer/non-buyer
- VARIABLE CODE PATTERNS: Question codes that suggest recoding relationships
- QUESTION TEXT ANALYSIS: Content that obviously describes transformations

RECODE GROUPING STRATEGY:
PREFER SPECIFIC RECODES over general transformations:
- Better: Separate age bands, income tiers, geographic regions
- Worse: One general demographic recode
- Better: Specific brand categories, spend levels, behavior segments
- Worse: One massive customer classification
- Identify natural recode subpatterns from questionnaire logic

COMPREHENSIVE RECODE STRATEGY:
1. EXPLICIT RECODES: Found directly in questionnaire with clear variable names
2. INFERRED RECODES: Logical recodes that SHOULD exist based on survey structure
3. CLASSIFICATION EXHAUSTIVE: Simple binary + complex tier classifications
4. EXACT TEXT WITH CONTEXT: Include actual questionnaire text + reformulation

MANDATORY RECODE DETECTION:
- Look for ALL classification logic (explicit + implicit)
- Find quota rules: who qualifies for what survey path/segment
- Detect buyer classifications: spending thresholds, behavior patterns
- MULTIPLE CLASSIFICATION LEVELS: Both basic + detailed versions may exist

OUTPUT SCHEMA (JSON array only):
[
  {
    "question_code": "Q1",
    "question_text": "Which brands do you know?",
    "type": "multi", 
    "possible_answers": {"1": "Brand A", "2": "Brand B", "3": "Brand C"},
    "grouping_hint": "Short reason why this is a multi-select group"
  },
  {
    "question_code": "AGE_RECODE",
    "question_text": "Age groups", 
    "type": "single",
    "possible_answers": {"1": "18-34", "2": "35-54", "3": "55+"},
    "recode_from": ["AGE"],
    "recode_hint": "QUESTIONNAIRE TEXT: 'exact text' | CONTEXT: explanation"
  }
]

CRITICAL SUCCESS FACTORS:
- Find ALL classification logic: quota rules, buyer segmentation, targeting logic
- DETECT IMPLICIT RECODES: business classifications not explicitly marked as "recode"
- BREAK DOWN into specific recode types when possible (separate age bands, income tiers, etc.)
- Use variable code patterns and question text to identify obvious recode relationships
- Look for spend/behavior patterns that create respondent categories

HINT RULES:
- Multi-select questions: Add "grouping_hint" only 
- Recode variables: Add "recode_hint" only (no grouping_hint for recodes)
"""

    thinking_prompt = f"""
    Think deeply about recode variable detection.
    Use your full reasoning capacity to find ALL transformation patterns.
    
    {prompt}
    
    Analyze systematically for comprehensive recode detection.
    """
    
    response = model.generate_content([thinking_prompt, uploaded_file])
    # Don't delete here - will delete after both functions complete
    
    try:
        result = json.loads(response.text)
        if isinstance(result, dict) and 'variables' in result:
            result = result['variables']
        elif not isinstance(result, list):
            result = []
        progress_print(f"Recodes: {len(result)} patterns found ({time.time() - start_time:.1f}s)", "success")
        return result
    except:
        progress_print(f"Recode analysis failed ({time.time() - start_time:.1f}s)", "error")
        return []

def main():
    if len(sys.argv) != 2:
        print("Usage: python step2_extract_questionnaire_metadata.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
        print(f"Error: PDF file not found or invalid: {pdf_path}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Step 2: Questionnaire Metadata Extraction")
    print(f"{'='*60}\n")
    
    total_start = time.time()
    
    try:
        # Upload PDF once before parallel execution
        progress_print("Uploading PDF to Gemini API", "info")
        upload_start = time.time()
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
        progress_print(f"PDF uploaded ({time.time() - upload_start:.1f}s)", "success")
        
        # Launch both analyses in parallel with the same uploaded file
        progress_print("Analyzing questionnaire (parallel processing)", "info")
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit both tasks with the same uploaded file
            multi_future = executor.submit(find_multiselect_questions, uploaded_file)
            recode_future = executor.submit(find_recode_variables, uploaded_file)
            
            # Wait for both to complete
            multiselect_patterns = multi_future.result()
            recode_patterns = recode_future.result()
        
        # Clean up uploaded file after both analyses complete
        genai.delete_file(uploaded_file)
        
        # Combine results
        all_patterns = []
        all_patterns.extend(multiselect_patterns)
        all_patterns.extend(recode_patterns)
        
        progress_print(f"Combined: {len(multiselect_patterns)} multi-select + {len(recode_patterns)} recodes", "success")
        
        # Save results
        
        output_path = Path('Output') / f"{pdf_path.stem}_questionnaire_metadata.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_patterns, f, indent=2, ensure_ascii=False)
        
        progress_print(f"Results saved to: {output_path}", "success")
        progress_print(f"Total execution time: {time.time() - total_start:.1f}s", "info")
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Execution time: {time.time() - total_start:.1f}s")
        sys.exit(1)

if __name__ == "__main__":
    main()