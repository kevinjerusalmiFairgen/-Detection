#!/usr/bin/env python3
"""
Complete Detection Pipeline - Runs all 3 steps automatically
Usage: python run_pipeline.py <data_file> <questionnaire_pdf>
"""

import sys
import time
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return timing info"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        print(f"✅ {description} completed in {elapsed:.1f}s")
        return elapsed, True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"❌ {description} failed after {elapsed:.1f}s")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return elapsed, False

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_pipeline.py <data_file> <questionnaire_pdf>")
        print("\nExamples:")
        print('  python run_pipeline.py "Data/IBIS/SkyConsulting_IBIS_Data.sav" "Data/IBIS/SkyConsulting_IBIS_QNR.docx - Google Docs.pdf"')
        print('  python run_pipeline.py "Data/ifop-fine-jewelery/ifop-fine-jewelery.sav" "Data/ifop-fine-jewelery/ifop-fine-jewelery.pdf"')
        print('  python run_pipeline.py "Data/Strat7 - Allergies/strat7_Allergies_data.xlsx" "Data/Strat7 - Allergies/strat7_Allergies_QNR.docx - Google Docs.pdf"')
        sys.exit(1)
    
    data_file = sys.argv[1]
    questionnaire_pdf = sys.argv[2]
    
    # Extract dataset name from data file
    data_path = Path(data_file)
    dataset_name = data_path.stem
    
    # Output file paths
    step1_output = f"Output/{dataset_name}_metadata.json"
    step2_output = f"Output/{Path(questionnaire_pdf).stem}_questionnaire_metadata.json"
    step3_output = f"Output/{dataset_name}_final_structure.json"
    
    print(f"\n🚀 DETECTION PIPELINE - {dataset_name.upper()}")
    print(f"📊 Data: {data_file}")
    print(f"📄 Questionnaire: {questionnaire_pdf}")
    
    total_start = time.time()
    
    # Step 1: Extract SPSS/Excel metadata
    step1_cmd = f'python step1_extract_spss_metadata.py --input "{data_file}" --output "{step1_output}"'
    step1_time, step1_success = run_command(step1_cmd, "STEP 1: Data Metadata Extraction")
    
    if not step1_success:
        print("❌ Pipeline failed at Step 1")
        sys.exit(1)
    
    # Step 2: Extract questionnaire metadata
    step2_cmd = f'python step2_extract_questionnaire_metadata.py "{questionnaire_pdf}"'
    step2_time, step2_success = run_command(step2_cmd, "STEP 2: Questionnaire Analysis")
    
    if not step2_success:
        print("❌ Pipeline failed at Step 2")
        sys.exit(1)
    
    # Step 3: Create final structure
    step3_cmd = f'python step3_create_final_structure.py "{step1_output}" "{step2_output}"'
    step3_time, step3_success = run_command(step3_cmd, "STEP 3: Final Structure Creation")
    
    if not step3_success:
        print("❌ Pipeline failed at Step 3")
        sys.exit(1)
    
    # Summary
    total_time = time.time() - total_start
    
    print(f"\n{'='*60}")
    print(f"🎉 PIPELINE COMPLETE - {dataset_name.upper()}")
    print(f"{'='*60}")
    print(f"Step 1 (Data): {step1_time:.1f}s")
    print(f"Step 2 (PDF): {step2_time:.1f}s") 
    print(f"Step 3 (Structure): {step3_time:.1f}s")
    print(f"{'='*60}")
    print(f"TOTAL TIME: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"{'='*60}")
    print(f"📁 Final Output: {step3_output}")
    
    # Check if final file exists and show size
    if Path(step3_output).exists():
        file_size = Path(step3_output).stat().st_size
        print(f"📊 File Size: {file_size:,} bytes")
        
        # Try to show basic stats
        try:
            import json
            with open(step3_output) as f:
                data = json.load(f)
            # Support both old and new key formats
            groups = len(data.get('multiSelect', data.get('groups', [])))
            recodes = len(data.get('recodings', data.get('recoding', [])))
            print(f"🔍 Results: {groups} groups + {recodes} recodes")
        except:
            pass

if __name__ == "__main__":
    main()


