#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Vahan RTO Dashboard..."
source venv/bin/activate
streamlit run app.py
