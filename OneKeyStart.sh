#!/bin/bash

# Connect the World, Frame by Frame - VideoLingo Startup Script

# Configuration
ENV_NAME="videolingo"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting VideoLingo...${NC}"

# 1. Find conda
CONDA_PATH=$(which conda)
if [ -z "$CONDA_PATH" ]; then
    # Standard location guesses
    for path in "$HOME/opt/anaconda3/bin/conda" "$HOME/anaconda3/bin/conda" "$HOME/miniconda3/bin/conda" "/usr/local/bin/conda" "/opt/homebrew/bin/conda"; do
        if [ -f "$path" ]; then
            CONDA_PATH="$path"
            break
        fi
    done
fi

if [ -z "$CONDA_PATH" ]; then
    echo -e "${RED}❌ Conda not found.${NC}"
    echo "Please install Miniconda or Anaconda first, or ensure 'conda' is in your PATH."
    exit 1
fi

# 2. Check if environment exists
ENV_EXISTS=$("$CONDA_PATH" env list | grep "^$ENV_NAME " )
if [ -z "$ENV_EXISTS" ]; then
    echo -e "${YELLOW}⚠️  Conda environment '$ENV_NAME' not found.${NC}"
    echo "Please run 'python install.py' first to initialize the project."
    exit 1
fi

# 3. Suppress TorchAudio warning and run Streamlit
echo -e "${GREEN}✅ Environment found. Launching UI...${NC}"
export TORCHAUDIO_USE_BACKEND_DISPATCHER=1

# Use 'conda run' to execute without manual activation
"$CONDA_PATH" run -n "$ENV_NAME" --no-capture-output python -m streamlit run st.py
