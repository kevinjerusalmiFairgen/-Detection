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
from api_keys import GEMINI_API_KEY

def find_multiselect_questions(pdf_path):
    """Specialized analysis for multi-select questions only"""
    start_time = time.time()
    print(f"[1/5] Finding multi-select questions")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json"
    )
    
    try:
        generation_config.thinking_tokens = 4000  # Max thinking tokens for large PDFs
    except:
        pass
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config=generation_config,
        system_instruction="You are an expert survey methodology detective with deep knowledge of questionnaire design. Focus ONLY on finding multi-select questions."
    )
    
    file = genai.upload_file(pdf_path, mime_type="application/pdf")
    
    prompt = """
OBJECTIVE: Find ALL multi-select questions (questions where respondent can choose multiple options)

MULTI-SELECT DETECTION PATTERNS:
- Explicit text: "Select all that apply", "Check all", "Multiple answers", "Mark all"
- Grid layouts: Multiple columns with same response scale  
- Lists of items/brands/features where multiple can be selected
- Programming clues: Conditional logic, loops, arrays indicate multi-structure

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
- Use programming text as primary intelligence source
- Clean programming prefixes from possible_answers
- Return comprehensive results
"""

    thinking_prompt = f"""
    Think deeply about multi-select question detection.
    Use your full reasoning capacity to find ALL multi-select patterns.
    
    {prompt}
    
    Analyze systematically for comprehensive multi-select detection.
    """
    
    response = model.generate_content([thinking_prompt, file])
    genai.delete_file(file)
    
    try:
        result = json.loads(response.text)
        if isinstance(result, dict) and 'variables' in result:
            result = result['variables']
        elif not isinstance(result, list):
            result = []
        print(f"[1/5] ✓ Multi-select analysis complete: {len(result)} patterns ({time.time() - start_time:.1f}s)")
        return result
    except:
        print(f"[1/5] ✓ Multi-select analysis failed ({time.time() - start_time:.1f}s)")
        return []

def find_recode_variables(pdf_path):
    """Specialized analysis for recode variables only"""
    start_time = time.time()
    print(f"[2/5] Finding recode variables")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json"
    )
    
    try:
        generation_config.thinking_tokens = 4000  # Max thinking tokens for large PDFs
    except:
        pass
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config=generation_config,
        system_instruction="You are an expert survey methodology detective specializing in recode detection. Focus ONLY on finding variable transformations and computed variables."
    )
    
    file = genai.upload_file(pdf_path, mime_type="application/pdf")
    
    prompt = """
OBJECTIVE: Find ALL recode variables (survey responses transformed/grouped into new variables)

RECODE DETECTION PATTERNS:
- Detailed responses grouped into broader categories
- Numerical data converted to ranges/bands
- Multiple variables combined into indices
- Geographic data aggregated to regions
- HIDDEN LOGIC: Implicit classification rules (quota, segmentation, targeting)
- BUSINESS LOGIC: Survey ops create classifications like buyer/non-buyer

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
    "question_code": "AGE_RECODE",
    "question_text": "Age groups", 
    "type": "single",
    "possible_answers": {"1": "18-34", "2": "35-54", "3": "55+"},
    "recode_from": ["AGE"],
    "recode_hint": "QUESTIONNAIRE TEXT: 'exact text explaining logic' | CONTEXT: reformulated explanation with context and business rules",
    "grouping_hint": "Short reason why this is identified as a recode transformation"
  }
]

CRITICAL SUCCESS FACTORS:
- Find ALL classification logic: quota rules, buyer segmentation, targeting logic
- DETECT IMPLICIT RECODES: business classifications not explicitly marked as "recode"
- Look for spend/behavior patterns that create respondent categories
- For ALL recode_hint: Include exact questionnaire text + clear reformulation
"""

    thinking_prompt = f"""
    Think deeply about recode variable detection.
    Use your full reasoning capacity to find ALL transformation patterns.
    
    {prompt}
    
    Analyze systematically for comprehensive recode detection.
    """
    
    response = model.generate_content([thinking_prompt, file])
    genai.delete_file(file)
    
    try:
        result = json.loads(response.text)
        if isinstance(result, dict) and 'variables' in result:
            result = result['variables']
        elif not isinstance(result, list):
            result = []
        print(f"[2/5] ✓ Recode analysis complete: {len(result)} patterns ({time.time() - start_time:.1f}s)")
        return result
    except:
        print(f"[2/5] ✓ Recode analysis failed ({time.time() - start_time:.1f}s)")
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
        # Split analysis for better focus
        print(f"[1/5] Split analysis: multi-select + recodes simultaneously")
        
        # Launch both analyses in parallel
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit both tasks simultaneously
            multi_future = executor.submit(find_multiselect_questions, pdf_path)
            recode_future = executor.submit(find_recode_variables, pdf_path)
            
            # Wait for both to complete
            multiselect_patterns = multi_future.result()
            recode_patterns = recode_future.result()
        
        # Combine results
        print(f"[3/5] Combining results")
        combine_start = time.time()
        
        all_patterns = []
        all_patterns.extend(multiselect_patterns)
        all_patterns.extend(recode_patterns)
        
        print(f"[3/5] ✓ Combined: {len(multiselect_patterns)} multi + {len(recode_patterns)} recodes ({time.time() - combine_start:.1f}s)")
        
        # Save results
        print(f"[4/5] Saving metadata")
        save_start = time.time()
        
        output_path = Path('Output') / f"{pdf_path.stem}_questionnaire_metadata.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_patterns, f, indent=2, ensure_ascii=False)
        
        print(f"[4/5] ✓ Metadata saved ({time.time() - save_start:.1f}s)")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✓ Extraction Complete!")
        print(f"{'='*60}")
        
        # Count by type
        types_count = {}
        for item in all_patterns:
            item_type = item.get('type', 'unknown')
            types_count[item_type] = types_count.get(item_type, 0) + 1
        
        print(f"Total patterns: {len(all_patterns)}")
        for type_name, count in sorted(types_count.items()):
            print(f"  - {type_name}: {count}")
        
        print(f"\nMulti-select analysis time: Check output above")
        print(f"Recode analysis time: Check output above") 
        print(f"Total execution time: {time.time() - total_start:.1f}s")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Execution time: {time.time() - total_start:.1f}s")
        sys.exit(1)

if __name__ == "__main__":
    main()