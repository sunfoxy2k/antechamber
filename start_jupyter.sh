#!/bin/bash

# Script to start Jupyter Lab with the virtual environment activated
# Usage: ./start_jupyter.sh

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting JupyterLab..."
echo "JupyterLab will open in your default browser."
echo "To stop the server, press Ctrl+C"
echo ""

# Start JupyterLab
jupyter lab --ip=localhost --port=8888 --no-browser

# Note: Remove --no-browser flag if you want Jupyter to open automatically in browser
