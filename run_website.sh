#!/usr/bin/env bash
# Launch the BeltGuard Streamlit website on Linux / macOS

cd "$(dirname "$0")"

echo "==========================================="
echo "  BeltGuard Streamlit Website Launcher"
echo "==========================================="

if ! python -c "import streamlit" 2>/dev/null; then
    echo "[setup] streamlit not found — installing dependencies..."
    python3 -m pip install -r requirements.txt
fi

echo "[run] starting streamlit server on http://localhost:8501 ..."
echo "      press Ctrl+C to stop"
echo ""
python3 -m streamlit run streamlit_app.py