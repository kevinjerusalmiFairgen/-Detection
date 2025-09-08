#!/usr/bin/env python3
"""
Step 3: Create final structured output by matching step2 findings with step1 variables
"""

import json
import sys
import time
from pathlib import Path
import google.generativeai as genai
from utils import get_api_key, progress_print

def find_groups_only(step1_input, step2_data):
    """Find groups only with debug"""
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config=generation_config,
        system_instruction="Survey data organizer. Use step2 guidance to find variable groups in step1. Output only step1 variable codes."
    )
    
    # Use ALL step1 and step2 data - no filtering!
    if isinstance(step1_input, list):
        step1_metadata = step1_input  # codes only
    else:
        step1_metadata = step1_input  # full metadata
    
    
    prompt = f"""
🔍 DETECTIVE MISSION: Find ALL MULTISELECT GROUPS from survey metadata

You are a survey methodology detective. Analyze the FULL step1 metadata to identify ALL variables that belong together as multiselect groups. 

Use step2 patterns as hints, but also discover additional groups step2 may have missed!

STEP1 METADATA: {json.dumps(step1_metadata)}

STEP2 CLUES (ALL questionnaire patterns): {json.dumps(step2_data)}

🕵️ DETECTIVE ANALYSIS REQUIRED:
1. **QUESTION TEXT SIMILARITY**: Look for similar question stems, contexts, topics
2. **LOGICAL GROUPING**: Variables measuring same concept (brands, features, occasions, etc.)
3. **ANSWER PATTERNS**: Similar possible_answers structure suggests related variables  
4. **CODE PATTERNS**: Related codes often share prefixes but NOT ALWAYS
5. **CONTEXTUAL LOGIC**: Use business/survey logic - what makes sense to group?

🎯 MULTISELECT DETECTION CLUES:
- Multiple variables asking about same topic (brands, activities, preferences)
- Same question stem with different options/sub-items
- Variables that logically go together (all measuring same construct)
- Step2 patterns provide hints found in questionnaire
- **BEYOND STEP2**: Find additional groups NOT in step2 but obvious from step1 metadata:
  * Code stem patterns (Q1_1, Q1_2, Q1_3 → Q1 group even if step2 missed it)
  * Identical/similar question text with different sub-options
  * Logical groupings that make business sense

⚡ CRITICAL RULES:
- Groups must have 2+ variables that LOGICALLY belong together
- Don't group random variables just because codes are similar
- Use metadata intelligence: question_text + possible_answers + context
- Each group should represent choices/options for same underlying question
- **DETECTIVE MANDATE**: Find ALL multiselect groups, including those step2 missed
  * Scan entire step1 metadata for obvious code patterns (Q1_1, Q1_2, etc.)
  * Identify question text similarities that indicate grouped options
  * Don't limit yourself to only step2 hints - be a thorough detective!

 OUTPUT (only meaningful multiselect groups):
 [
   {{"id": "0", "name": "0", "columns": ["var1", "var2", "var3"]}}
 ]
"""

    try:
        response = model.generate_content(prompt)
        
        if hasattr(response, 'text') and response.text:
            try:
                result = json.loads(response.text)
                return result
            except:
                return []
        else:
            return []
            
    except:
        return []

def find_recodes_only(step1_input, step2_data):
    """Find recodes only"""
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json",
    }
    
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config=generation_config,
        system_instruction="Survey data organizer. Use step2 guidance to find recode relationships in step1. Output only step1 variable codes."
    )
    
    # Filter step2 for recode patterns only
    recode_patterns = [p for p in step2_data if p.get('recode_from') or p.get('recode_hint')]
    
    prompt = f"""
 TASK: Find recode relationships using step2 recode guidance.
 
 STEP1: {json.dumps(step1_input)}
 STEP2 RECODE PATTERNS: {json.dumps(recode_patterns)}
 
 Use step2 to understand source→target relationships in step1.
 Find which step1 variables are recoded INTO other step1 variables.
 
 OUTPUT (recodes only):
 [
   {{"id": "12", "name": "12", "recode": "TARGET_COLUMN_FROM_STEP1", "codes": ["SOURCE_COLUMN_FROM_STEP1"]}}
 ]
 
 CRITICAL: 
 - "recode" field MUST be a column name that exists in step1 data
 - "codes" field MUST contain column names that exist in step1 data
 - Use step2 patterns to identify which step1 variables are sources and which are targets
"""

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text) if response.text else []
    except:
        return []

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
    print(f"[1/4] Loading files")
    start_time = time.time()
    
    with open(step1_file, 'r') as f:
        step1_data = json.load(f)
    with open(step2_file, 'r') as f:
        step2_data = json.load(f)
    
    # Clean empty possible_answers
    cleaned_step1_data = []
    for item in step1_data:
        cleaned_item = item.copy()
        if not cleaned_item.get('possible_answers'):
            cleaned_item.pop('possible_answers', None)
        cleaned_step1_data.append(cleaned_item)
    
    step1_codes = [item['question_code'] for item in cleaned_step1_data]
    print(f"[1/4] ✓ Loaded {len(cleaned_step1_data)} step1 variables and {len(step2_data)} step2 patterns ({time.time() - start_time:.1f}s)")
    
    # Smart input sizing
    if len(cleaned_step1_data) > 1500:
        print(f"[2/4] Large dataset - using codes only")
        step1_input = step1_codes
    else:
        print(f"[2/4] Normal dataset - using full metadata")
        step1_input = cleaned_step1_data
    
    # Split analysis: groups and recodes separately
    print(f"[2/4] Split analysis: groups + recodes separately")
    
    # Find groups
    print(f"[2/4] Finding groups...")
    groups_start = time.time()
    groups = find_groups_only(step1_input, step2_data)
    print(f"[2/4] ✓ Groups found: {len(groups)} ({time.time() - groups_start:.1f}s)")
    
    # Find recodes
    print(f"[2/4] Finding recodes...")
    recodes_start = time.time()
    recodes = find_recodes_only(step1_input, step2_data)
    print(f"[2/4] ✓ Recodes found: {len(recodes)} ({time.time() - recodes_start:.1f}s)")
    
    # Create final structure in the required format
    final_structure = {
        "recodings": recodes,
        "multiSelect": groups,
        "typeOfNan": []
    }
    print(f"[2/4] ✓ Combined in Python: {len(groups)} groups + {len(recodes)} recodes")
    
    # Validate
    step1_codes_set = set(step1_codes)
    invalid_vars = []
    
    for group in final_structure.get('multiSelect', []):
        for var in group.get('columns', []):
            if var not in step1_codes_set:
                invalid_vars.append(f"Group: {var}")
    
    for recode in final_structure.get('recodings', []):
        # Check source codes exist in step1
        for var in recode.get('codes', []):
            if var not in step1_codes_set:
                invalid_vars.append(f"Recode source '{var}' not in step1")
        # Check target recode exists in step1
        target = recode.get('recode', '')
        if target and target not in step1_codes_set:
            invalid_vars.append(f"Recode target '{target}' not in step1")
    
    print(f"[3/4] Validation:")
    if invalid_vars:
        print(f"🚨 Found {len(invalid_vars)} variables NOT in step1 codes:")
        for var in invalid_vars[:10]:
            print(f"  - {var}")
        if len(invalid_vars) > 10:
            print(f"  ... and {len(invalid_vars) - 10} more")
    else:
        print(f"✅ All variables valid - only step1 codes used")
    
    # Save
    print(f"[4/4] Saving results")
    output_path = Path('Output') / f"{dataset_name}_final_structure.json"
    
    with open(output_path, 'w') as f:
        json.dump(final_structure, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Complete!")
    print(f"{'='*60}")
    print(f"Groups: {len(final_structure.get('multiSelect', []))}")
    print(f"Recodes: {len(final_structure.get('recodings', []))}")
    print(f"Total time: {time.time() - total_start:.1f}s")
    print(f"Output: {output_path}")

if __name__ == "__main__":
    main()