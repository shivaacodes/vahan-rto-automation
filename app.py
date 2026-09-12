import streamlit as st
import subprocess
import os
from datetime import datetime
import config

st.set_page_config(page_title="Vahan RTO Dashboard", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Push the entire page to the top — no default Streamlit padding */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        padding-bottom: 1rem;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Remove ALL vertical gaps inside columns */
    section[data-testid="stMain"] div[data-testid="stVerticalBlock"] {
        gap: 0.6rem !important;
    }
    /* But keep zero gap at the very top of the right column */
    div[data-testid="column"]:nth-child(2) > div > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        padding-top: 0 !important;
    }

    .title-header {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2D3748 !important;
        margin: 0 0 0.2rem 0;
        line-height: 1.2;
    }
    .subtitle {
        color: #94a3b8 !important;
        font-size: 0.88rem;
        margin: 0 0 1.4rem 0;
    }

    /* Slim uppercase section labels */
    .section-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #94a3b8;
        margin: 1rem 0 0.35rem 0;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        padding: 0.6rem 0.9rem !important;
        border-radius: 8px !important;
    }
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div {
        color: #1E293B !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }

    /* Button */
    .stButton>button {
        width: 100%;
        background-color: #0F172A;
        color: white;
        border-radius: 6px;
        padding: 0.6rem;
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        transition: background 0.2s ease;
        margin-top: 0.25rem;
    }
    .stButton>button:hover { background-color: #334155; color: white; border: none; }

    /* Green progress bar */
    div[data-testid="stProgressBar"] > div > div > div {
        background: linear-gradient(90deg, #22c55e, #16a34a) !important;
        border-radius: 9999px !important;
    }
    div[data-testid="stProgressBar"] > div {
        background-color: #dcfce7 !important;
        border-radius: 9999px !important;
    }

    /* Badges */
    @keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .live-badge {
        display:inline-flex; align-items:center; gap:6px;
        background:#dcfce7; color:#15803d; font-size:0.72rem; font-weight:600;
        padding:3px 10px; border-radius:9999px; border:1px solid #86efac;
    }
    .live-dot {
        width:8px; height:8px; border-radius:50%;
        background:#22c55e; animation:pulse-dot 1.2s ease-in-out infinite;
    }
    .done-badge {
        display:inline-flex; align-items:center; gap:6px;
        background:#f0fdf4; color:#166534; font-size:0.72rem; font-weight:600;
        padding:3px 10px; border-radius:9999px; border:1px solid #86efac;
    }

    /* Stat pills */
    .stat-bar { display:flex; gap:8px; margin-top:0.5rem; }
    .stat-pill {
        background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
        padding:5px 10px; font-size:0.78rem; font-weight:600;
        color:#1e293b; flex:1; text-align:center;
    }
    .stat-pill.green { background:#f0fdf4; border-color:#86efac; color:#166534; }
    .stat-pill.red   { background:#fff1f2; border-color:#fca5a5; color:#991b1b; }

    /* Mac Terminal */
    .mac-terminal {
        background:#1E1E1E; border-radius:8px;
        box-shadow:0 4px 16px rgba(0,0,0,0.18);
        overflow:hidden; font-family:'Menlo','Monaco','Courier New',monospace;
    }
    .mac-terminal-header {
        background:#2D2D2D; padding:9px 14px;
        display:flex; align-items:center;
        border-bottom:1px solid #111;
    }
    .mac-dots { display:flex; gap:7px; }
    .mac-dot  { width:12px; height:12px; border-radius:50%; }
    .mac-dot.red    { background:#FF5F56; }
    .mac-dot.yellow { background:#FFBD2E; }
    .mac-dot.green  { background:#27C93F; }
    .mac-terminal-title {
        color:#888; font-size:0.8rem; flex-grow:1;
        text-align:center; font-family:-apple-system,sans-serif;
        margin-right:42px;
    }
    .mac-terminal-body {
        padding:14px; color:#F8F8F2;
        font-size:0.82rem; line-height:1.7;
        white-space:pre-wrap;
        height: calc(100vh - 6.5rem);
        min-height: 500px;
        overflow-y:auto;
    }
    </style>
""", unsafe_allow_html=True)

# ── Split immediately — no full-width header above ───────────────────────────
left_col, right_col = st.columns([1, 1.6], gap="large")

date_str   = datetime.now().strftime("%Y-%m-%d")
output_dir = os.path.join(config.REPORTS_DIR, date_str)

# ════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — title + config + controls
# ════════════════════════════════════════════════════════════════════════════
with left_col:
    # Title (lives in left column)
    st.markdown('<div class="title-header">🏛️ Vahan Analytics Downloader</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Automated extraction system for daily RTO reports</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Active Configuration</div>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.metric("Target State", config.FILTERS['State'].split('(')[0].strip())
    with r1c2:
        st.metric("Report Year", config.FILTERS['Year'])
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.metric("Y-Axis Pivot", config.FILTERS['Y-Axis'])
    with r2c2:
        st.metric("X-Axis Pivot", config.FILTERS['X-Axis'])

    st.markdown('<div class="section-label">Output Destination</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;
                padding:10px 14px; font-family:'Menlo','Monaco',monospace;
                font-size:0.78rem; color:#475569; word-break:break-all;">
        📁 {output_dir}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Execution Control</div>', unsafe_allow_html=True)
    run_btn      = st.button("▶  Initialize Data Extraction", type="primary")
    progress_bar = st.empty()
    badge_cont   = st.empty()
    stat_cont    = st.empty()
    status_text  = st.empty()

# ════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — terminal, starts at the very top of the page
# ════════════════════════════════════════════════════════════════════════════
with right_col:
    log_container = st.empty()

    def render_terminal(body_html):
        log_container.markdown(f"""
        <div class="mac-terminal">
            <div class="mac-terminal-header">
                <div class="mac-dots">
                    <div class="mac-dot red"></div>
                    <div class="mac-dot yellow"></div>
                    <div class="mac-dot green"></div>
                </div>
                <div class="mac-terminal-title">bash — download_reports.py</div>
            </div>
            <div class="mac-terminal-body">{body_html}</div>
        </div>""", unsafe_allow_html=True)

    render_terminal('<span style="color:#6EE7B7;">vahan-bot \$</span> Waiting for extraction command...')

# ── Run logic ────────────────────────────────────────────────────────────────
if run_btn:
    render_terminal('<span style="color:#6EE7B7;">vahan-bot \$</span> Initializing Vahan Extraction Protocol...<br>')
    progress_bar.progress(0)
    badge_cont.markdown('<div class="live-badge"><div class="live-dot"></div> RUNNING</div>', unsafe_allow_html=True)

    log_output   = []
    saved_count  = 0
    failed_count = 0
    total_rtos   = 87

    process = subprocess.Popen(
        ["python", "-u", "download_reports.py"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )

    def colorize(line):
        p = '<span style="color:#6EE7B7;">vahan-bot \$</span> '
        if "Successfully saved" in line:
            return p + f'<span style="color:#4ADE80;">{line}</span>'
        elif "ERROR" in line or "Failed" in line or "Retry" in line:
            return p + f'<span style="color:#F87171;">{line}</span>'
        elif "WARNING" in line:
            return p + f'<span style="color:#FBBF24;">{line}</span>'
        elif "Found" in line and "RTOs" in line:
            return p + f'<span style="color:#60A5FA;">{line}</span>'
        return p + line

    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue
        log_output.append(colorize(line))
        render_terminal("<br>".join(log_output[-24:]))

        if "Found" in line and "RTOs to process" in line:
            try:
                total_rtos = int(line.split("Found ")[1].split(" ")[0])
            except:
                pass
        if "Successfully saved" in line:
            saved_count += 1
        if "Failed to process" in line or "Retry failed" in line:
            failed_count += 1

        done = saved_count + failed_count
        if done > 0:
            progress_bar.progress(min(done / total_rtos, 1.0))
        stat_cont.markdown(f"""
        <div class="stat-bar">
            <div class="stat-pill green">✅ {saved_count} saved</div>
            <div class="stat-pill red">❌ {failed_count} failed</div>
            <div class="stat-pill">{total_rtos - done} remaining</div>
        </div>""", unsafe_allow_html=True)
        status_text.markdown(f"**Progress:** `{done}` / `{total_rtos}` RTOs")

    process.stdout.close()
    rc = process.wait()

    if rc == 0:
        progress_bar.progress(1.0)
        badge_cont.markdown('<div class="done-badge">✅ COMPLETE</div>', unsafe_allow_html=True)
        stat_cont.markdown(f"""
        <div class="stat-bar">
            <div class="stat-pill green">✅ {saved_count} saved</div>
            <div class="stat-pill red">❌ {failed_count} failed</div>
            <div class="stat-pill">0 remaining</div>
        </div>""", unsafe_allow_html=True)
        status_text.success("All reports downloaded successfully!")
        st.balloons()
    else:
        badge_cont.markdown(
            '<div class="done-badge" style="background:#fff1f2;border-color:#fca5a5;color:#991b1b;">⚠️ HALTED</div>',
            unsafe_allow_html=True
        )
        status_text.error("Extraction halted — check terminal for details.")
