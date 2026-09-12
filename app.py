import streamlit as st
import subprocess
import os
from datetime import datetime
import config

# Must be the first Streamlit command
st.set_page_config(page_title="Vahan RTO Dashboard", page_icon="🏛️", layout="centered")

# Custom CSS for a modern, professional look
st.markdown("""
    <style>
    /* Hide Streamlit default branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Modernize typography and spacing */
    .main .block-container {
        padding-top: 2rem;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Style the main title */
    .title-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2D3748 !important;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #718096 !important;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Style the metrics cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }
    /* Force text color in metrics in case of dark mode conflicts */
    div[data-testid="metric-container"] label, 
    div[data-testid="metric-container"] div {
        color: #1E293B !important;
    }
    
    /* Style the run button */
    .stButton>button {
        width: 100%;
        background-color: #0F172A;
        color: white;
        border-radius: 6px;
        padding: 0.75rem;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #334155;
        border: none;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="title-header">🏛️ Vahan Analytics Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated extraction system for daily RTO reports</div>', unsafe_allow_html=True)
st.divider()

# Configuration Metrics Section
st.markdown("### Active Configuration")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Target State", value=config.FILTERS['State'].split('(')[0].strip())
with col2:
    st.metric(label="Report Year", value=config.FILTERS['Year'])
with col3:
    st.metric(label="Y-Axis Pivot", value=config.FILTERS['Y-Axis'])
with col4:
    st.metric(label="X-Axis Pivot", value=config.FILTERS['X-Axis'])

st.write("") # Spacer

# Output Information
date_str = datetime.now().strftime("%Y-%m-%d")
output_dir = os.path.join(config.REPORTS_DIR, date_str)

st.info(f"📁 **Output Destination:** `{output_dir}`", icon="ℹ️")

# Control Section
st.markdown("### Execution Control")

if st.button("Initialize Data Extraction", type="primary"):
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # We put the logs in an expander so it doesn't clutter the modern UI
    with st.expander("Terminal Output (Live Logs)", expanded=True):
        log_container = st.empty()
    
    log_output = []
    
    # Run the existing script as a subprocess
    process = subprocess.Popen(
        ["python", "-u", "download_reports.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    processed_count = 0
    total_rtos = 87 
    
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue
            
        log_output.append(line)
        
        # Keep only last 12 lines for the UI to stay clean
        display_logs = "\n".join(log_output[-12:])
        log_container.code(display_logs, language="text")
        
        # Update progress based on log messages
        if "Found" in line and "RTOs to process" in line:
            try:
                total_rtos = int(line.split("Found ")[1].split(" ")[0])
            except:
                pass
                
        if "Successfully saved" in line or "Failed to process" in line:
            processed_count += 1
            progress_pct = min(processed_count / total_rtos, 1.0)
            progress_bar.progress(progress_pct)
            status_text.markdown(f"**Status:** Processing `{processed_count}` of `{total_rtos}` records...")
            
    process.stdout.close()
    return_code = process.wait()
    
    if return_code == 0:
        progress_bar.progress(1.0)
        status_text.success(f"✅ **Extraction Complete.** All files are secured in the output directory.")
        st.balloons()
    else:
        status_text.error("⚠️ **Extraction Halted.** The system encountered a critical error. Please review the terminal output.")
