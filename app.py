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
    
    /* Mac Terminal Window */
    .mac-terminal {
        background-color: #1E1E1E;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        overflow: hidden;
        margin-top: 1rem;
        font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    }
    .mac-terminal-header {
        background-color: #323232;
        padding: 8px 12px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #111;
    }
    .mac-dots {
        display: flex;
        gap: 6px;
    }
    .mac-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .mac-dot.red { background-color: #FF5F56; }
    .mac-dot.yellow { background-color: #FFBD2E; }
    .mac-dot.green { background-color: #27C93F; }
    .mac-terminal-title {
        color: #999;
        font-size: 0.85rem;
        flex-grow: 1;
        text-align: center;
        font-family: -apple-system, sans-serif;
        margin-right: 42px; /* balance the dots width */
    }
    .mac-terminal-body {
        padding: 12px;
        color: #F8F8F2;
        font-size: 0.85rem;
        line-height: 1.5;
        white-space: pre-wrap;
        height: 250px;
        overflow-y: auto;
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
    
    # We put the logs in a custom Mac-like terminal window
    log_container = st.empty()
    
    def render_terminal(logs_text):
        terminal_html = f"""
        <div class="mac-terminal">
            <div class="mac-terminal-header">
                <div class="mac-dots">
                    <div class="mac-dot red"></div>
                    <div class="mac-dot yellow"></div>
                    <div class="mac-dot green"></div>
                </div>
                <div class="mac-terminal-title">bash — download_reports.py</div>
            </div>
            <div class="mac-terminal-body">{logs_text}</div>
        </div>
        """
        log_container.markdown(terminal_html, unsafe_allow_html=True)
        
    render_terminal("Initializing Vahan Extraction Protocol...<br>")
    
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
        display_logs = "<br>".join(log_output[-12:])
        render_terminal(display_logs)
        
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
