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
from api_keys import GEMINI_API_KEY

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
    You are an expert survey data analyst specializing in intelligent variable matching.
    
    INPUT SOURCES WITH DIFFERENT PRECISION:
    
    STEP1 (SPSS METADATA - ABSOLUTE TRUTH):
    - Actual SPSS variable codes extracted from data files
    - 100% accurate variable names and descriptions
    - ONLY valid source for output variable names
    
    STEP2 (PDF ANALYSIS - IDEAS ONLY):
    - PDF questionnaire analysis results - not hard coded variables, so not reliable for output variable names
    - Provides structural insights and recode logic as guidance
    - Variable names are HINTS for finding actual step1 variables
    - Step2 is less precise because PDF ≠ actual data structure
    
    MATCHING INTELLIGENCE:
    - Step2 provides WHAT to look for (patterns, logic, relationships)
    - Step1 provides the ACTUAL variables that exist
    - Your job: connect step2 insights with step1 reality
    - Step2 naming might be imprecise - use semantic understanding for matching
    
    ABSOLUTE RULE: Output contains ONLY step1 variable codes.
    """
    
    # Configure generation without output limits for large datasets
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json"
    )
    
    # Add minimal thinking tokens to avoid limits
    try:
        generation_config.thinking_tokens = 800  # Minimal thinking for efficiency
    except:
        pass
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    
    # Upload JSON files as text/plain
    print(f"[2/4] Uploading step1 metadata to Gemini")
    with open(step1_file, 'rb') as f:
        step1_upload = genai.upload_file(f, mime_type="text/plain")
    
    print(f"[2/4] Uploading step2 patterns to Gemini") 
    with open(step2_file, 'rb') as f:
        step2_upload = genai.upload_file(f, mime_type="text/plain")

    prompt = """
Match step2 patterns with step1 variables.

INPUTS:
- STEP1: Real SPSS variable codes (truth)
- STEP2: Questionnaire analysis patterns (guidance)

TASK: Create groups and recodes using ONLY step1 variable codes.

OUTPUT FORMAT:
{
  "groups": [{"id": "group_0", "name": "question text", "columns": ["var1", "var2"]}],
  "recoding": [{"id": "id", "name": "target_var", "codes": ["source1", "source2"], "recode": "target_var"}]
}

CRITICAL: codes/recode/columns = ONLY variable codes (A07r1, B12, hQuota), NO descriptions.
"""

    print(f"[2/4] Analyzing {dataset_name} with uploaded files")
    analysis_start = time.time()
    response = model.generate_content([prompt, step1_upload, step2_upload])
    print(f"[2/4] ✓ Analysis complete ({time.time() - analysis_start:.1f}s)")
    print(f"[2/4] Execution time: {time.time() - start_time:.1f}s")
    
    # Clean up uploaded files
    genai.delete_file(step1_upload)
    genai.delete_file(step2_upload)
    
    try:
        if hasattr(response, 'text') and response.text:
            result = json.loads(response.text)
            return result
        else:
            finish_reason = response.candidates[0].finish_reason if response.candidates else 'unknown'
            if finish_reason == 2:
                print(f"Warning: Model hit max tokens limit (finish_reason: 2)")
                print("Output may be incomplete due to size limitations")
            else:
                print(f"Warning: Empty response from Gemini (finish_reason: {finish_reason})")
            return {"groups": [], "recoding": []}
    except json.JSONDecodeError as e:
        print(f"Warning: JSON parse error: {e}")
        return {"groups": [], "recoding": []}
    except Exception as e:
        print(f"Warning: Response error: {e}")
        return {"groups": [], "recoding": []}

def validate_output_variables(result, step1_data):
    """Validate that all output variables exist in step1"""
    step1_codes = {item['question_code'] for item in step1_data}
    invalid_vars = []
    
    # Check groups
    if 'groups' in result:
        for group in result['groups']:
            for var_code in group.get('columns', []):
                if var_code not in step1_codes:
                    invalid_vars.append(f"Group column: {var_code}")
    
    # Check recoding
    if 'recoding' in result:
        for recode in result['recoding']:
            # Check codes field
            for var_code in recode.get('codes', []):
                if var_code not in step1_codes:
                    invalid_vars.append(f"Recode codes: {var_code}")
            
            # Check recode field
            recode_var = recode.get('recode', '')
            if recode_var and recode_var not in step1_codes:
                invalid_vars.append(f"Recode target: {recode_var}")
    
    if invalid_vars:
        print(f"🚨 VALIDATION FAILED! Found {len(invalid_vars)} invalid variables:")
        for var in invalid_vars[:10]:  # Show first 10
            print(f"  - {var}")
        if len(invalid_vars) > 10:
            print(f"  ... and {len(invalid_vars) - 10} more")
    else:
        print(f"✅ Validation passed! All variables are from step1")

def save_final_structure(result, output_path):
    """Save final structured output"""
    start_time = time.time()
    print(f"[4/4] Saving final structure to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[4/4] ✓ Final structure saved ({time.time() - start_time:.1f}s)")

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
        
        # Validate all variables are from step1
        print(f"[3/4] Validating output variables")
        validate_output_variables(result, step1_data)
        
        # Save final structure
        output_path = Path('Output') / f"{dataset_name}_final_structure.json"
        output_path.parent.mkdir(exist_ok=True)
        save_final_structure(result, output_path)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✓ Final Structure Complete!")
        print(f"{'='*60}")
        
        # Handle both dict and list formats
        if isinstance(result, dict):
            groups_count = len(result.get('groups', []))
            recodes_count = len(result.get('recoding', []))
            print(f"Groups created: {groups_count}")
            print(f"Recodes created: {recodes_count}")
        elif isinstance(result, list):
            print(f"Total questions returned: {len(result)}")
            print("Note: Expected groups/recoding format, got list of questions")
        else:
            print("Unexpected result format")
        
        print(f"\nTotal execution time: {time.time() - total_start:.1f}s")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Execution time: {time.time() - total_start:.1f}s")
        sys.exit(1)

if __name__ == "__main__":
    main()