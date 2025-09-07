#!/usr/bin/env python3
"""
Step 2: Extract metadata from questionnaire PDFs using Gemini Flash
Focus: Identify multi-select questions and recode mappings
"""

import json
import sys
import time
from pathlib import Path
import google.generativeai as genai
from api_keys import GEMINI_API_KEY

def analyze_pdf_with_gemini(pdf_path):
    """Send PDF to Gemini to identify multi-select questions and recodes"""
    start_time = time.time()
    
    print(f"[1/3] Configuring Gemini API")
    genai.configure(api_key=GEMINI_API_KEY)
    
    file_size = pdf_path.stat().st_size
    print(f"[1/3] Processing {file_size:,} byte PDF file")
    
    system_instruction = """
    You are an expert survey methodology detective with deep knowledge of questionnaire design and programming.
    
    CRITICAL THINKING PROCESS:
    1. ANALYZE each question thoroughly - what is the TRUE intent?
    2. REASON through programming logic - what does the code reveal?
    3. DETECT patterns and structures that aren't immediately obvious
    4. DISTINGUISH between direct questions vs computed/transformed variables
    5. THINK like a survey programmer - what would require computation vs direct asking?
    
    Use maximum reasoning to uncover ALL multi-select questions and genuine recodes.
    Think step-by-step through each variable's purpose and origin.
    """
    
    # Try to configure thinking tokens for maximum reasoning
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json"
    )
    
    # Add thinking tokens if supported
    try:
        generation_config.thinking_tokens = 4000  # Max thinking tokens for large PDFs
    except:
        pass  # Model will use default thinking capacity
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-1219",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    
    print(f"[2/3] Uploading PDF to Gemini")
    upload_start = time.time()
    file = genai.upload_file(pdf_path, mime_type="application/pdf")
    print(f"[2/3] ✓ PDF uploaded ({time.time() - upload_start:.1f}s)")
    
    prompt = """
INPUTS
- PDF questionnaire document

OBJECTIVE
- BE A DETECTIVE: Use reasoning and clues to find ALL multi-select and recodes
- THINK like a survey researcher: What variables are computed vs directly asked?
- Use programming text, logic, and context as INTELLIGENCE sources
- LEVERAGE survey programming instructions as key insights into question structure

DETECTIVE REASONING FOR MULTI-SELECT
Think: Can respondent logically choose multiple options?
- Lists of items/brands/features = usually multi-select
- Mutually exclusive options = single-select
- Grid questions across categories = often multi-select

DETECTIVE REASONING FOR RECODES  
Think: Is this a transformation/mapping/computation of another/others survey response?
- Detailed responses grouped into broader categories
- Numerical data converted to ranges/bands
- Multiple variables combined into indices
- Geographic data aggregated to regions
- HIDDEN LOGIC: Look for implicit classification rules (quota, segmentation, targeting)
- BUSINESS LOGIC: Survey ops often create hidden classifications for analysis

CONTEXTUAL INTELLIGENCE  
- Look for variable pairs: detailed + grouped versions
- Common recode suffixes: groupings, bandings, categories
- IGNORE system tracking variables (not survey response transformations)

PROGRAMMING TEXT AS INTELLIGENCE
- Survey programming reveals the TRUE structure behind questions
- Use programming logic to understand what's really happening
- Conditional displays often indicate multi-select logic
- Recode instructions reveal variable transformations
- Loop structures suggest multi-select with follow-ups
- Programming comments and notes provide crucial insights
- HIDDEN CLASSIFICATIONS: Look for quota logic, segmentation rules, targeting criteria
- BUSINESS VARIABLES: Survey ops create classifications like buyer/non-buyer, qualified/unqualified

INTELLIGENCE-BASED SEARCH STRATEGY
1. READ BETWEEN THE LINES: What's implied but not explicitly stated?
2. SURVEY LOGIC: Would a human researcher ask this directly or compute it?
3. HIDDEN CLASSIFICATIONS: Look for quota logic, buyer vs non-buyer, qualified vs unqualified
4. SPEND-BASED SEGMENTATION: Find logic that classifies based on purchase amounts
5. IMPLICIT BUSINESS RECODES: Classification rules even without "recode" mentions
6. TARGETING VARIABLES: Logic that separates respondents for different questionnaire paths
7. THINK HOLISTICALLY: Consider ALL survey workflow and classification needs

OUTPUT SCHEMA:
{
  "variables": [
    {
      "question_code": "Q1",
      "question_text": "Question text",
      "type": "multi",
      "possible_answers": {"1": "Option 1", "2": "Option 2"}
    },
    {
      "question_code": "SOME_RECODE", 
      "type": "single", 
      "possible_answers": {"1": "Group 1", "2": "Group 2"},
      "recode_from": ["SOURCE_VAR"],
      "recode_hint": "EXACT questionnaire text explaining the classification logic and rules"
    }
  ],
  "potential_recodes": [
    {
      "hint": "Description of likely recode pattern",
      "likely_sources": ["source variable types"],
      "search_terms": ["keywords to help find in step1"]
    }
  ]
}

For recodes: ALWAYS include recode_from + recode_hint with:
1. EXACT questionnaire text (quoted verbatim)
2. REFORMULATED explanation with full context for clarity
3. SPECIFIC conditions, thresholds, and business rules

ADD INFERENCE SECTION: At the end, add "potential_recodes" with hints for ALL likely recodes:
{
  "potential_recodes": [
    {
      "hint": "Basic buyer vs non-buyer quota classification based on spending behavior",
      "likely_sources": ["spend questions", "purchase behavior"],
      "search_terms": ["quota", "buyer", "classification"]
    }
  ]
}

COMPREHENSIVE RECODE STRATEGY:
1. EXPLICIT RECODES: Found directly in questionnaire with clear variable names
2. INFERRED RECODES: Logical recodes that SHOULD exist based on survey structure
3. CLASSIFICATION EXHAUSTIVE: For every classification concept, look for ALL possible versions
4. EXACT TEXT WITH CONTEXT: For recode_hint, include actual questionnaire text + reformulation
   - Quote the exact questionnaire text that explains the recode logic
   - Reformulate with full context if original text lacks clarity
   - Include specific thresholds, conditions, and business rules
   - Add surrounding context to make the logic crystal clear for step3

MANDATORY RECODE DETECTION:
- Look for ALL classification logic in questionnaire (explicit + implicit)
- Find quota rules: who qualifies for what survey path/segment
- Detect buyer classifications: spending thresholds, behavior patterns
- Identify targeting variables: demographic/psychographic groupings
- INFER missing recodes: Add logical recodes with descriptive hints for step3 to find

RESPONSE CLEANING RULES
- Remove ALL programming prefixes: "IF..:", "SHOW IF:", "ASK ONLY:", "DISPLAY IF:"
- Extract only the actual response text after the colon
- Example: "IF AGE<25: Student discounts" → "Student discounts"

CRITICAL SUCCESS FACTORS
- Extract explicit multi-select and recode patterns found in questionnaire
- INFER additional likely recodes based on survey structure and logic
- For ALL recode_hint: Include exact questionnaire text + clear reformulation
- Provide comprehensive guidance with original text + contextual explanation
- Clean programming prefixes from response text

RECODE_HINT FORMAT:
"QUESTIONNAIRE TEXT: 'exact text from PDF explaining logic' | CONTEXT: reformulated explanation with full context, specific thresholds, and business rules"
    """
    
    print(f"[2/3] Analyzing with Gemini Flash (using maximum reasoning)")
    analysis_start = time.time()
    
    # Configure for maximum thinking
    thinking_prompt = f"""
    Think deeply and methodically about this questionnaire analysis task.
    Use your full reasoning capacity to analyze every aspect carefully.
    
    {prompt}
    
    Take your time to think through each variable systematically.
    """
    
    response = model.generate_content([thinking_prompt, file])
    print(f"[2/3] ✓ Analysis complete ({time.time() - analysis_start:.1f}s)")
    
    # Clean up
    genai.delete_file(file)
    
    # Parse response
    try:
        result = json.loads(response.text)
        if isinstance(result, dict):
            # Handle single object or wrapped response
            if 'variables' in result:
                result = result['variables']
            elif 'questions' in result:
                result = result['questions']
            elif 'question_code' in result:
                result = [result]
            else:
                # Try to extract array from dict
                for key, value in result.items():
                    if isinstance(value, list):
                        result = value
                        break
        print(f"[2/3] Execution time: {time.time() - start_time:.1f}s")
        return result if isinstance(result, list) else []
    except json.JSONDecodeError as e:
        print(f"Warning: JSON parse error: {e}")
        print(f"Response preview: {response.text[:500]}...")
        print(f"[2/3] Execution time: {time.time() - start_time:.1f}s")
        return []

def save_metadata(metadata, output_path):
    """Save metadata to JSON file"""
    start_time = time.time()
    print(f"[3/3] Saving metadata to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[3/3] ✓ Saved successfully ({time.time() - start_time:.1f}s)")

def main():
    """Main function"""
    total_start = time.time()
    
    if len(sys.argv) != 2:
        print("Usage: python step2_extract_questionnaire_metadata.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    if pdf_path.suffix.lower() != '.pdf':
        print(f"Error: Input must be a PDF file")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Step 2: Questionnaire Metadata Extraction")
    print(f"{'='*60}\n")
    
    try:
        # Analyze PDF
        metadata = analyze_pdf_with_gemini(pdf_path)
        
        # Save results
        output_path = Path('Output') / f"{pdf_path.stem}_questionnaire_metadata.json"
        output_path.parent.mkdir(exist_ok=True)
        save_metadata(metadata, output_path)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✓ Extraction Complete!")
        print(f"{'='*60}")
        
        # Count by type
        types_count = {}
        for item in metadata:
            item_type = item.get('type', 'unknown')
            types_count[item_type] = types_count.get(item_type, 0) + 1
        
        print(f"Questions extracted: {len(metadata)}")
        for type_name, count in types_count.items():
            print(f"  - {type_name}: {count}")
        
        print(f"\nTotal execution time: {time.time() - total_start:.1f}s")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Execution time: {time.time() - total_start:.1f}s")
        sys.exit(1)

if __name__ == "__main__":
    main()