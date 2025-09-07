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
    
    # Configure model with thinking abilities
    print(f"[2/3] Analyzing with deep thinking capabilities")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Configure for deep semantic analysis
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        response_mime_type="application/json"
    )
    
    try:
        generation_config.thinking_tokens = 8000  # Deep thinking for semantic matching
    except:
        pass
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config=generation_config,
        system_instruction="Expert survey analyst with deep thinking abilities. Use question_code + question_text + possible_answers from step1 to find semantic relationships with step2 patterns. Output ONLY step1 variable codes."
    )
    
    # Create simple prompt
    # Show hidden variables examples to guide target finding
    hidden_vars = [code for code in step1_codes if code.startswith('h')]
    
    prompt = f"""
SEMANTIC MATCHING WITH DEEP THINKING:

Use your thinking abilities to analyze step1 metadata and find relationships with step2 patterns.

STEP1 COMPLETE METADATA (question_code + question_text + possible_answers):
{json.dumps(step1_data)}

STEP2 PATTERNS WITH HINTS:
{json.dumps(step2_data)}

THINKING PROCESS FOR EACH STEP2 PATTERN:
1. READ step2 pattern description and grouping_hint
2. ANALYZE step1 question_text for content similarity
3. EXAMINE step1 possible_answers for pattern matches
4. THINK about survey logic and relationships
5. FIND step1 variables that represent the same concepts

Use question_code + question_text + possible_answers to make intelligent semantic matches.

OUTPUT (use ONLY step1 question_codes):
{{
  "groups": [
    {{"id": "group_0", "name": "description", "columns": ["step1_question_code1", "step1_question_code2"]}}
  ],
  "recoding": [
    {{"id": "recode_0", "name": "step1_target_code", "codes": ["step1_source_code"], "recode": "step1_target_code"}}
  ]
}}

CRITICAL: Use ONLY question_code values from step1 metadata above.
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
        print(f"🚨 VALIDATION FAILED! Found {len(invalid_vars)} variables NOT in step1 codes:")
        for var in invalid_vars:
            print(f"  - {var}")
        print(f"\nThese variables are NOT step1 codes and violate the rule!")
    else:
        print(f"✅ All variables valid - only step1 codes used")
    
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