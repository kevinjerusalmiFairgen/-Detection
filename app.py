#!/usr/bin/env python3
"""
Detection Pipeline - Streamlit Web App
Upload data files and questionnaire PDFs to get multiselect groups detection
"""

import streamlit as st
import tempfile
import json
import time
import subprocess
import os
from pathlib import Path
import zipfile
import io

# Page config
st.set_page_config(
    page_title="Detection Pipeline",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def run_pipeline_step(cmd, step_name):
    """Run a pipeline step and capture output"""
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=os.getcwd()
        )
        
        elapsed = time.time() - start_time
        
        return {
            'success': True,
            'elapsed': elapsed,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'step': step_name
        }
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        
        return {
            'success': False,
            'elapsed': elapsed,
            'stdout': e.stdout or '',
            'stderr': e.stderr or '',
            'step': step_name,
            'error': str(e)
        }

def create_download_zip(results, step_outputs):
    """Create a ZIP file with all results and debug info"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Add final structure JSON
        if step_outputs.get('step3') and os.path.exists(step_outputs['step3']):
            zip_file.write(step_outputs['step3'], 'final_structure.json')
        
        # Add intermediate files
        if step_outputs.get('step1') and os.path.exists(step_outputs['step1']):
            zip_file.write(step_outputs['step1'], 'step1_metadata.json')
            
        if step_outputs.get('step2') and os.path.exists(step_outputs['step2']):
            zip_file.write(step_outputs['step2'], 'step2_questionnaire_metadata.json')
        
        # Add debug logs
        debug_info = {
            'pipeline_summary': {
                'total_time': sum(r['elapsed'] for r in results.values()),
                'steps_completed': len([r for r in results.values() if r['success']]),
                'steps_failed': len([r for r in results.values() if not r['success']])
            },
            'step_details': results
        }
        
        zip_file.writestr('debug_info.json', json.dumps(debug_info, indent=2))
        
        # Add step logs as text files
        for step_name, result in results.items():
            log_content = f"""
=== {step_name.upper()} LOG ===
Success: {result['success']}
Time: {result['elapsed']:.1f}s

=== STDOUT ===
{result['stdout']}

=== STDERR ===
{result['stderr']}

=== ERROR ===
{result.get('error', 'None')}
"""
            zip_file.writestr(f'{step_name}_log.txt', log_content)
    
    zip_buffer.seek(0)
    return zip_buffer

def main():
    st.title("🔍 Detection Pipeline")
    st.markdown("**Upload your data files to detect multiselect groups automatically**")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 File Upload")
        
        # Data file upload
        data_file = st.file_uploader(
            "Data File (.sav, .xlsx, .csv)",
            type=['sav', 'xlsx', 'xls', 'csv'],
            help="Upload your SPSS (.sav) or Excel (.xlsx) data file"
        )
        
        # Questionnaire PDF upload
        pdf_file = st.file_uploader(
            "Questionnaire PDF",
            type=['pdf'],
            help="Upload the questionnaire PDF file"
        )
        
        st.markdown("---")
        
        # Process button
        process_button = st.button(
            "🚀 Run Pipeline", 
            type="primary",
            disabled=not (data_file and pdf_file)
        )
    
    # Main content
    if not (data_file and pdf_file):
        st.info("👆 Please upload both files in the sidebar to start")
        
        # Show examples
        st.markdown("### 📋 Supported File Types")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Data Files:**")
            st.markdown("- SPSS (.sav)")
            st.markdown("- Excel (.xlsx, .xls)")
            st.markdown("- CSV (.csv)")
        
        with col2:
            st.markdown("**Questionnaire:**")
            st.markdown("- PDF (.pdf)")
        
        return
    
    # Show uploaded files info
    st.markdown("### 📊 Uploaded Files")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Data:** {data_file.name} ({data_file.size:,} bytes)")
    
    with col2:
        st.info(f"**PDF:** {pdf_file.name} ({pdf_file.size:,} bytes)")
    
    # Process pipeline
    if process_button:
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded files
            data_path = temp_path / data_file.name
            pdf_path = temp_path / pdf_file.name
            
            with open(data_path, 'wb') as f:
                f.write(data_file.getbuffer())
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_file.getbuffer())
            
            # Output paths
            dataset_name = data_path.stem
            step1_output = f"Output/{dataset_name}_metadata.json"
            step2_output = f"Output/{pdf_path.stem}_questionnaire_metadata.json"
            step3_output = f"Output/{dataset_name}_final_structure.json"
            
            step_outputs = {
                'step1': step1_output,
                'step2': step2_output, 
                'step3': step3_output
            }
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Results container
            results = {}
            
            # Step 1: Data metadata extraction
            status_text.text("🔄 Step 1: Extracting data metadata...")
            progress_bar.progress(10)
            
            step1_cmd = f'python step1_extract_spss_metadata.py --input "{data_path}" --output "{step1_output}"'
            results['step1'] = run_pipeline_step(step1_cmd, "Step 1: Data Metadata")
            
            if not results['step1']['success']:
                st.error(f"❌ Step 1 failed: {results['step1'].get('error', 'Unknown error')}")
                st.code(results['step1']['stderr'], language='text')
                return
            
            progress_bar.progress(40)
            
            # Step 2: Questionnaire analysis
            status_text.text("🔄 Step 2: Analyzing questionnaire PDF...")
            
            step2_cmd = f'python step2_extract_questionnaire_metadata.py "{pdf_path}"'
            results['step2'] = run_pipeline_step(step2_cmd, "Step 2: Questionnaire Analysis")
            
            if not results['step2']['success']:
                st.error(f"❌ Step 2 failed: {results['step2'].get('error', 'Unknown error')}")
                st.code(results['step2']['stderr'], language='text')
                return
            
            progress_bar.progress(70)
            
            # Step 3: Final structure creation
            status_text.text("🔄 Step 3: Creating final structure...")
            
            step3_cmd = f'python step3_create_final_structure.py "{step1_output}" "{step2_output}"'
            results['step3'] = run_pipeline_step(step3_cmd, "Step 3: Final Structure")
            
            if not results['step3']['success']:
                st.error(f"❌ Step 3 failed: {results['step3'].get('error', 'Unknown error')}")
                st.code(results['step3']['stderr'], language='text')
                return
            
            progress_bar.progress(100)
            status_text.text("✅ Pipeline completed successfully!")
            
            # Show results
            st.success("🎉 Pipeline completed successfully!")
            
            # Summary metrics
            total_time = sum(r['elapsed'] for r in results.values())
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Time", f"{total_time:.1f}s")
            
            with col2:
                st.metric("Step 1", f"{results['step1']['elapsed']:.1f}s")
            
            with col3:
                st.metric("Step 2", f"{results['step2']['elapsed']:.1f}s")
            
            with col4:
                st.metric("Step 3", f"{results['step3']['elapsed']:.1f}s")
            
            # Show final results if available
            if os.path.exists(step3_output):
                try:
                    with open(step3_output) as f:
                        final_data = json.load(f)
                    
                    groups_count = len(final_data.get('groups', []))
                    recodes_count = len(final_data.get('recoding', []))
                    
                    st.markdown("### 📊 Results Summary")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Groups Found", groups_count)
                    
                    with col2:
                        st.metric("Recodes Found", recodes_count)
                    
                    # Show sample groups
                    if groups_count > 0:
                        st.markdown("### 🔍 Sample Groups")
                        sample_groups = final_data['groups'][:3]  # Show first 3
                        
                        for i, group in enumerate(sample_groups):
                            with st.expander(f"Group {i+1}: {group.get('name', 'Unnamed')}"):
                                st.write(f"**Variables:** {len(group.get('columns', []))}")
                                st.code(', '.join(group.get('columns', [])[:10]), language='text')
                                if len(group.get('columns', [])) > 10:
                                    st.write(f"... and {len(group.get('columns', [])) - 10} more")
                
                except Exception as e:
                    st.warning(f"Could not parse final results: {e}")
            
            # Download section
            st.markdown("### 📥 Download Results")
            
            # Create download ZIP
            zip_buffer = create_download_zip(results, step_outputs)
            
            st.download_button(
                label="📦 Download All Results (ZIP)",
                data=zip_buffer,
                file_name=f"{dataset_name}_detection_results.zip",
                mime="application/zip",
                type="primary"
            )
            
            # Individual file downloads
            if os.path.exists(step3_output):
                with open(step3_output) as f:
                    final_json = f.read()
                
                st.download_button(
                    label="📄 Download Final Structure (JSON)",
                    data=final_json,
                    file_name=f"{dataset_name}_final_structure.json",
                    mime="application/json"
                )
            
            # Debug info expander
            with st.expander("🔧 Debug Information"):
                for step_name, result in results.items():
                    st.markdown(f"**{step_name.upper()}**")
                    
                    if result['success']:
                        st.success(f"✅ Completed in {result['elapsed']:.1f}s")
                    else:
                        st.error(f"❌ Failed after {result['elapsed']:.1f}s")
                    
                    if result['stdout']:
                        st.code(result['stdout'], language='text')
                    
                    if result['stderr']:
                        st.code(result['stderr'], language='text')
                    
                    st.markdown("---")

if __name__ == "__main__":
    main()
