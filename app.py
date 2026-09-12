import streamlit as st
import subprocess
import os
from datetime import datetime
import config

# Must be the first Streamlit command
st.set_page_config(page_title="Vahan RTO Dashboard", page_icon="🏛️", layout="wide")

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
        padding-left: 2.5rem;
        padding-right: 2.5rem;
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
        margin-top: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #334155;
        border: none;
        color: white;
    }

    /* Left panel separator */
    .left-panel {
        padding-right: 1.5rem;
        border-right: 1px solid #E2E8F0;
    }

    /* Mac Terminal Window */
    .mac-terminal {
        background-color: #1E1E1E;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        overflow: hidden;
        font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
        height: 100%;
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
        margin-right: 42px;
    }
    .mac-terminal-body {
        padding: 14px;
        color: #F8F8F2;
        font-size: 0.82rem;
        line-height: 1.6;
        white-space: pre-wrap;
        height: 340px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown('<div class="title-header">🏛️ Vahan Analytics Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated extraction system for daily RTO reports</div>', unsafe_allow_html=True)
st.divider()

# ── Configuration Metrics (full width, above the split) ─────────────────────
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

st.write("")  # Spacer

# ── Two-column layout: Control | Terminal ─────────────────────────────────
date_str = datetime.now().strftime("%Y-%m-%d")
output_dir = os.path.join(config.REPORTS_DIR, date_str)

left_col, right_col = st.columns([1, 1.6], gap="large")

# ── LEFT: Execution Control ──────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown("### Execution Control")
    st.info(f"📁 **Output Destination:**\n`{output_dir}`", icon="ℹ️")
    st.write("")

    run_btn = st.button("▶  Initialize Data Extraction", type="primary")

    progress_bar  = st.empty()
    status_text   = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT: Mac Terminal ───────────────────────────────────────────────────────
with right_col:
    st.markdown("### Live Terminal Output")
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

    # Show idle terminal on page load
    render_terminal('<span style="color:#6EE7B7;">vahan-bot \$</span> Waiting for extraction command...')

# ── Run logic (only triggers when button is clicked) ─────────────────────────
if run_btn:
    render_terminal('<span style="color:#6EE7B7;">vahan-bot \$</span> Initializing Vahan Extraction Protocol...<br>')
    progress_bar.progress(0)

    log_output = []

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

        display_lines = log_output[-18:]  # more lines since terminal is taller
        display_logs = '<span style="color:#6EE7B7;">vahan-bot \$</span> ' + \
                       '<br><span style="color:#6EE7B7;">vahan-bot \$</span> '.join(display_lines)
        render_terminal(display_logs)

        if "Found" in line and "RTOs to process" in line:
            try:
                total_rtos = int(line.split("Found ")[1].split(" ")[0])
            except:
                pass

        if "Successfully saved" in line or "Failed to process" in line:
            processed_count += 1
            progress_pct = min(processed_count / total_rtos, 1.0)
            progress_bar.progress(progress_pct)
            status_text.markdown(f"**Status:** `{processed_count}` / `{total_rtos}` RTOs processed")

    process.stdout.close()
    return_code = process.wait()

    if return_code == 0:
        progress_bar.progress(1.0)
        status_text.success("✅ **Extraction Complete.** All files secured in output directory.")
        st.balloons()
    else:
        status_text.error("⚠️ **Extraction Halted.** Check terminal output for details.")
