# Medical Agent System

A multi-agent medical office system built with LiveKit and Coral Protocol for patient triage, support, billing, and documentation.

## Features

- **Triage Agent**: Initial patient assessment and routing
- **Support Agent**: Appointment scheduling and general inquiries  
- **Billing Agent**: Insurance and payment assistance
- **Notes Agent**: Session documentation and record management

## Quick Start

1. **Setup Environment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Create directories and prompts
   python setup.py
   
   # Copy and configure environment
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start Coral Server**
   Make sure your Coral server is running on `localhost:5555`

3. **Run the Medical Agent**
   ```bash
   python medical_agent.py
   ```

## Configuration

### Required API Keys
- **Groq API Key**: For LLM processing
- **Deepgram API Key**: For speech-to-text
- **Cartesia API Key**: For text-to-speech  
- **LiveKit Credentials**: For voice communication

### Environment Variables
See `.env.example` for all configuration options.

## Directory Structure

```
├── medical_agent.py      # Main agent system
├── utils.py             # Utility functions
├── setup.py             # Setup script
├── requirements.txt     # Dependencies
├── patient_data/        # Patient notes storage
├── prompts/             # Agent prompt configurations
└── logs/                # System logs
```

## Usage

1. **Start with Triage**: Patients begin with the Triage Agent
2. **Transfer Between Agents**: Agents can transfer patients as needed
3. **Save Notes**: Use Notes Agent to document sessions
4. **Review History**: Access previous patient sessions

## Notes Storage

Patient notes are automatically saved to `patient_data/` as YAML files with:
- Patient information and session data
- Timestamped interactions
- Agent transfer history
- Comprehensive documentation

## Customization

- **Modify Prompts**: Edit files in `prompts/` directory
- **Add Agents**: Extend the system by creating new agent classes
- **Configure LLMs**: Switch between Groq, OpenAI, and other providers

## Support

For issues with:
- LiveKit integration: Check LiveKit documentation
- Coral Protocol: Reference Coral Protocol docs  
- Agent behavior: Modify prompt files in `prompts/`
