#!/usr/bin/env python3
"""
Step 3: Create final structured output by matching step2 findings with step1 variables
"""

import json
import sys
import time
from pathlib import Path
import google.generativeai as genai
from api_keys import GEMINI_API_KEY

def main():
    if len(sys.argv) != 3:
        print("Usage: python step3_create_final_structure.py <step1_metadata.json> <step2_questionnaire_metadata.json>")
        sys.exit(1)
    
    step1_file = Path(sys.argv[1])
    step2_file = Path(sys.argv[2])
    dataset_name = step1_file.stem.replace('_metadata', '')
    
    print(f"\n{'='*60}")
    print(f"Step 3: Final Structure Creation - {dataset_name}")
    print(f"{'='*60}\n")
    
    total_start = time.time()
    
    # Load data
    print(f"[1/3] Loading files")
    start_time = time.time()
    
    with open(step1_file, 'r') as f:
        step1_data = json.load(f)
    with open(step2_file, 'r') as f:
        step2_data = json.load(f)
    
    step1_codes = [item['question_code'] for item in step1_data]
    print(f"[1/3] ✓ Loaded {len(step1_data)} step1 variables and {len(step2_data)} step2 patterns ({time.time() - start_time:.1f}s)")
    
    # Configure model
    print(f"[2/3] Analyzing with Gemini")
    genai.configure(api_key=GEMINI_API_KEY)
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config={
            "temperature": 0.1,
            "response_mime_type": "application/json",
        },
        system_instruction="Expert survey analyst. Match step2 patterns with step1 actual variables. Use only step1 variable codes in output."
    )
    
    # Create simple prompt
    prompt = f"""
Match step2 patterns with step1 variables.

STEP1 VARIABLE CODES: 
{json.dumps(step1_codes)}

STEP2 PATTERNS:
{json.dumps(step2_data)}

OUTPUT FORMAT:
{{
  "groups": [
    {{"id": "group_0", "name": "description", "columns": ["step1_var1", "step1_var2"]}}
  ],
  "recoding": [
    {{"id": "recode_0", "name": "target_var", "codes": ["source_var"], "recode": "target_var"}}
  ]
}}

CRITICAL: Use ONLY step1 variable codes in columns/codes/recode fields.
"""

    # Analyze
    analysis_start = time.time()
    response = model.generate_content(prompt)
    print(f"[2/3] ✓ Analysis complete ({time.time() - analysis_start:.1f}s)")
    
    # Parse result
    try:
        result = json.loads(response.text)
    except:
        print("Failed to parse response")
        result = {"groups": [], "recoding": []}
    
    # Validate
    step1_codes_set = set(step1_codes)
    invalid_vars = []
    
    for group in result.get('groups', []):
        for var in group.get('columns', []):
            if var not in step1_codes_set:
                invalid_vars.append(f"Group: {var}")
    
    for recode in result.get('recoding', []):
        for var in recode.get('codes', []):
            if var not in step1_codes_set:
                invalid_vars.append(f"Recode codes: {var}")
        target = recode.get('recode', '')
        if target and target not in step1_codes_set:
            invalid_vars.append(f"Recode target: {target}")
    
    if invalid_vars:
        print(f"🚨 Found {len(invalid_vars)} invalid variables")
    else:
        print(f"✅ All variables valid")
    
    # Save
    print(f"[3/3] Saving results")
    output_path = Path('Output') / f"{dataset_name}_final_structure.json"
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Complete!")
    print(f"{'='*60}")
    print(f"Groups: {len(result.get('groups', []))}")
    print(f"Recodes: {len(result.get('recoding', []))}")
    print(f"Total time: {time.time() - total_start:.1f}s")
    print(f"Output: {output_path}")

if __name__ == "__main__":
    main()