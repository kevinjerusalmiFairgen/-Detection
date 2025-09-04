#!/usr/bin/env python3
"""
Step 3: Create final structured output by matching step2 findings with step1 variables
Uses step1 metadata as TRUTH and step2 results as structure intelligence
"""

import json
import sys
import time
from pathlib import Path
import google.generativeai as genai
from secrets import GEMINI_API_KEY

def load_metadata_files(step1_file, step2_file):
    """Load step1 and step2 results"""
    start_time = time.time()
    print(f"[1/4] Loading metadata files")
    
    with open(step1_file, 'r', encoding='utf-8') as f:
        step1_data = json.load(f)
    
    with open(step2_file, 'r', encoding='utf-8') as f:
        step2_data = json.load(f)
    
    print(f"[1/4] ✓ Loaded {len(step1_data)} step1 variables and {len(step2_data)} step2 patterns ({time.time() - start_time:.1f}s)")
    return step1_data, step2_data

def analyze_with_gemini(step1_file, step2_file, dataset_name):
    """Use Gemini to intelligently match patterns with actual variables"""
    start_time = time.time()
    print(f"[2/4] Configuring Gemini for intelligent variable matching")
    genai.configure(api_key=GEMINI_API_KEY)
    
    system_instruction = """
    You are an expert survey data analyst specializing in finding variable relationships.
    
    CRITICAL UNDERSTANDING:
    - Step1 contains ALL actual variable codes (ONLY source of truth for variable names)
    - Step2 provides insights/patterns to help FIND variables in step1
    - Step2 variable names are just hints - DO NOT use them in output
    - Your job: use step2 insights to discover actual step1 variable relationships
    
    PROCESS:
    1. Read step2 patterns to understand what to look for
    2. Search step1 variables to find actual variable codes
    3. Use step2 recode_hint descriptions to identify relationships
    4. Output ONLY step1 variable codes
    5. Never copy variable names from step2
    
    ABSOLUTE RULE: Output contains ONLY step1 variable codes.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
            "response_mime_type": "application/json",
        },
        system_instruction=system_instruction
    )
    
    try:
        # Try file upload approach first
        print(f"[2/4] Uploading step1 metadata to Gemini")
        with open(step1_file, 'rb') as f:
            step1_upload = genai.upload_file(f, mime_type="application/json")
        
        print(f"[2/4] Uploading step2 patterns to Gemini") 
        with open(step2_file, 'rb') as f:
            step2_upload = genai.upload_file(f, mime_type="application/json")

        prompt = """
INTELLIGENT MATCHING TASK:
You have two uploaded JSON files:
1. STEP1: Actual SPSS variable metadata (ground truth)
2. STEP2: Questionnaire patterns found from PDF analysis

TASK:
Match step2 patterns with step1 actual variables through semantic understanding.

SMART MATCHING + INTELLIGENCE DISCOVERY:
1. MATCH: Connect step2 patterns with step1 actual variables  
2. USE RECODE HINTS: Step2 provides recode_hint descriptions to help find variables
3. CONTENT ANALYSIS: Analyze step1 question text for additional clues
4. PATTERN DISCOVERY: Use matches as templates for additional patterns
5. RECODE VALIDATION: ALL recodes must have valid source variables (recode_from)

CRITICAL RECODE RULE:
Every recode MUST have source variables. If you can't find source variables in step1, don't include the recode.

OUTPUT FORMAT - STEP1 VARIABLES ONLY:
{
  "groups": [
    {
      "id": "step1_var_code",
      "name": "step1_var_code", 
      "columns": ["step1_var_1", "step1_var_2"]
    }
  ],
  "recoding": [
    {
      "id": "step1_target_var",
      "name": "step1_target_var",
      "source_vars": ["step1_source_var"],
      "codes": ["step1_source_var"],
      "recode": "step1_target_var"
    }
  ]
}

CRITICAL RULE: 
- NEVER use step2 variable names in output
- ONLY use variable codes that exist in step1
- Step2 provides insights to FIND step1 variables, not provide variable names
"""

        print(f"[2/4] Analyzing {dataset_name} with uploaded files")
        analysis_start = time.time()
        response = model.generate_content([prompt, step1_upload, step2_upload])
        print(f"[2/4] ✓ Analysis complete ({time.time() - analysis_start:.1f}s)")
        
        # Clean up uploaded files
        genai.delete_file(step1_upload)
        genai.delete_file(step2_upload)
        
    except Exception as e:
        print(f"[2/4] File upload failed ({e}), falling back to embedded data")
        
        # Fallback: Load data and embed in prompt
        with open(step1_file, 'r', encoding='utf-8') as f:
            step1_data = json.load(f)
        with open(step2_file, 'r', encoding='utf-8') as f:
            step2_data = json.load(f)
            
        prompt = f"""
STEP2 INSIGHTS → STEP1 VARIABLE DISCOVERY

Step2 provides insights about what to look for. Use these insights to find actual step1 variables.

STEP1 VARIABLES (832 total - ONLY source for output):
{json.dumps([item['question_code'] for item in step1_data], indent=2)}

STEP2 INSIGHTS (what to look for):
{json.dumps(step2_data, indent=2)}

PROCESS:
1. Use step2 insights to understand what patterns exist
2. Search step1 variables to find actual codes that match these patterns
3. Use step2 recode_hints to find source→target relationships in step1
4. Group step1 variables based on step2 structural insights

CRITICAL: Step2 variable names are just hints. Output only contains step1 variable codes.

OUTPUT FORMAT:
{{
  "groups": [...],
  "recoding": [...]
}}
"""

        print(f"[2/4] Analyzing {dataset_name} with embedded data")
        analysis_start = time.time()
        response = model.generate_content(prompt)
        print(f"[2/4] ✓ Analysis complete ({time.time() - analysis_start:.1f}s)")
    
    print(f"[2/4] Execution time: {time.time() - start_time:.1f}s")
    
    try:
        if hasattr(response, 'text') and response.text:
            result = json.loads(response.text)
            return result
        else:
            print(f"Warning: Empty response from Gemini")
            return {"groups": [], "recoding": []}
    except json.JSONDecodeError as e:
        print(f"Warning: JSON parse error: {e}")
        return {"groups": [], "recoding": []}
    except Exception as e:
        print(f"Warning: Response error: {e}")
        return {"groups": [], "recoding": []}

def save_final_structure(result, output_path):
    """Save final structured output"""
    start_time = time.time()
    print(f"[3/4] Saving final structure to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[3/4] ✓ Final structure saved ({time.time() - start_time:.1f}s)")

def main():
    """Main function"""
    total_start = time.time()
    
    if len(sys.argv) != 3:
        print("Usage: python step3_create_final_structure.py <step1_metadata.json> <step2_questionnaire_metadata.json>")
        print("\nExample:")
        print('  python step3_create_final_structure.py Output/jewelry_metadata.json "Output/ifop-fine-jewelery_questionnaire_metadata.json"')
        sys.exit(1)
    
    step1_file = Path(sys.argv[1])
    step2_file = Path(sys.argv[2]) 
    
    # Validate inputs
    if not step1_file.exists():
        print(f"Error: Step1 file not found: {step1_file}")
        sys.exit(1)
        
    if not step2_file.exists():
        print(f"Error: Step2 file not found: {step2_file}")
        sys.exit(1)
    
    dataset_name = step1_file.stem.replace('_metadata', '')
    
    print(f"\n{'='*60}")
    print(f"Step 3: Final Structure Creation")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*60}\n")
    
    try:
        # Load metadata files for summary info
        step1_data, step2_data = load_metadata_files(step1_file, step2_file)
        
        # Analyze and match with Gemini (pass file paths directly)
        result = analyze_with_gemini(step1_file, step2_file, dataset_name)
        
        # Save final structure
        output_path = Path('Output') / f"{dataset_name}_final_structure.json"
        output_path.parent.mkdir(exist_ok=True)
        save_final_structure(result, output_path)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✓ Final Structure Complete!")
        print(f"{'='*60}")
        
        groups_count = len(result.get('groups', []))
        recodes_count = len(result.get('recoding', []))
        
        print(f"Groups created: {groups_count}")
        print(f"Recodes created: {recodes_count}")
        
        if groups_count > 0:
            total_columns = sum(len(group.get('columns', [])) for group in result['groups'])
            print(f"Total variables in groups: {total_columns}")
        
        print(f"\nTotal execution time: {time.time() - total_start:.1f}s")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Execution time: {time.time() - total_start:.1f}s")
        sys.exit(1)

if __name__ == "__main__":
    main()
