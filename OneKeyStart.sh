#!/bin/bash

# Connect the World, Frame by Frame - VideoLingo macOS Startup Script

# Configuration
ENV_NAME="videolingo"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting VideoLingo (macOS)...${NC}"

# Find conda
CONDA_PATH=$(which conda)
if [ -z "$CONDA_PATH" ]; then
    for path in "/opt/homebrew/bin/conda" "$HOME/anaconda3/bin/conda" "$HOME/miniconda3/bin/conda" "/usr/local/bin/conda"; do
        if [ -f "$path" ]; then
            CONDA_PATH="$path"
            break
        fi
    done
fi

if [ -z "$CONDA_PATH" ]; then
    echo -e "${RED}❌ Conda not found.${NC}"
    echo "Please ensure 'conda' is in your PATH or installed via Homebrew."
    exit 1
fi

# Check if environment exists
ENV_EXISTS=$("$CONDA_PATH" env list | grep "^$ENV_NAME " )
if [ -z "$ENV_EXISTS" ]; then
    echo -e "${YELLOW}⚠️  Conda environment '$ENV_NAME' not found.${NC}"
    echo "Running 'bash run_installer.sh' to initialize the project..."
    bash run_installer.sh
    exit $?
fi

echo -e "${GREEN}✅ Environment found. Launching UI...${NC}"
export TORCHAUDIO_USE_BACKEND_DISPATCHER=1

# Use 'conda run' for clean execution
"$CONDA_PATH" run -n "$ENV_NAME" --no-capture-output python -m streamlit run st.py
