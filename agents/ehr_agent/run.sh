#!/bin/bash

# Exit on error
set -e

echo "🏥 Starting EHR Agent..."

# Check if we're in the VitalMesh conda environment
if [[ "$CONDA_DEFAULT_ENV" != "VitalMesh" ]]; then
    echo "❌ Error: Please activate the VitalMesh conda environment first"
    echo "Run: conda activate VitalMesh"
    exit 1
fi

echo "✅ Using VitalMesh conda environment"

# Install required packages in conda environment
echo "📥 Installing dependencies in conda environment..."
pip install -q groq python-dotenv pyyaml requests

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables..."
    # Use a safer method to load .env that handles comments
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            export "$line"
        fi
    done < .env
fi

# Set default environment variables if not already set
export LLM_PROVIDER=${LLM_PROVIDER:-"groq"}
export LLM_MODEL=${LLM_MODEL:-"llama-3.1-8b-instant"}
export CORAL_SSE_URL=${CORAL_SSE_URL:-"http://localhost:5555"}
export CORAL_AGENT_ID=${CORAL_AGENT_ID:-"ehr_agent"}
export TIMEOUT_MS=${TIMEOUT_MS:-"60000"}
export OUTPUT_DIR=${OUTPUT_DIR:-"./ehr_outputs"}

# Check if API key is set
if [ -z "$API_KEY" ]; then
    echo "❌ Error: API_KEY environment variable is not set"
    echo "Please set your Groq API key in the .env file or export it:"
    echo "export API_KEY=your_groq_api_key_here"
    exit 1
fi

echo "✅ Environment configured:"
echo "   LLM Provider: $LLM_PROVIDER"
echo "   LLM Model: $LLM_MODEL" 
echo "   Coral URL: $CORAL_SSE_URL"
echo "   Agent ID: $CORAL_AGENT_ID"
echo "   Output Dir: $OUTPUT_DIR"

# Run the agent
echo "🚀 Starting EHR Agent..."
python3 "$@"