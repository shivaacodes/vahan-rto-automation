import streamlit as st
import subprocess
import os
from datetime import datetime
import config

st.set_page_config(page_title="Vahan RTO Downloader", page_icon="📊", layout="centered")

st.title("🚗 Vahan RTO Report Downloader")
st.markdown("This dashboard automates downloading daily Excel reports for all 87 Kerala RTOs.")

# Sidebar with configuration
st.sidebar.header("Current Configuration")
st.sidebar.markdown(f"**State:** {config.FILTERS['State']}")
st.sidebar.markdown(f"**Year:** {config.FILTERS['Year']}")
st.sidebar.markdown(f"**Y-Axis:** {config.FILTERS['Y-Axis']}")
st.sidebar.markdown(f"**X-Axis:** {config.FILTERS['X-Axis']}")

# Paths
date_str = datetime.now().strftime("%Y-%m-%d")
output_dir = os.path.join(config.REPORTS_DIR, date_str)

st.write(f"**Today's Output Folder:** `{output_dir}`")

if st.button("▶️ Start Download", type="primary"):
    st.info("Starting automation in the background. Please do not close this window until finished.")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.empty()
    
    # We will capture logs to display them
    log_output = []
    
    # Run the existing script as a subprocess so we can capture stdout in real-time
    process = subprocess.Popen(
        ["python", "-u", "download_reports.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    processed_count = 0
    total_rtos = 87 # Default assumption, dynamically updated if we see it in logs
    
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue
            
        log_output.append(line)
        
        # Keep only last 15 lines for the UI to stay clean
        display_logs = "\n".join(log_output[-15:])
        log_container.code(display_logs, language="text")
        
        # Update progress based on log messages
        if "Found" in line and "RTOs to process" in line:
            try:
                # Example: "Found 87 RTOs to process."
                total_rtos = int(line.split("Found ")[1].split(" ")[0])
            except:
                pass
                
        if "Successfully saved" in line or "Failed to process" in line:
            processed_count += 1
            progress_pct = min(processed_count / total_rtos, 1.0)
            progress_bar.progress(progress_pct)
            status_text.text(f"Processed {processed_count} of {total_rtos} RTOs...")
            
    process.stdout.close()
    return_code = process.wait()
    
    if return_code == 0:
        progress_bar.progress(1.0)
        status_text.success(f"✅ Finished! All reports are saved in: {output_dir}")
    else:
        status_text.error("⚠️ The script exited with an error. Check the logs above.")
