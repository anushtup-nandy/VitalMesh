#!/usr/bin/env python3
"""
Setup script for Medical Agent System
Creates directory structure and example prompt files
"""

import os
import yaml
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        'patient_data',
        'prompts',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}/")

def create_prompt_files():
    """Create example prompt files"""
    
    # Triage Agent Prompt
    triage_prompt = {
        'instructions': """You are a professional Medical Triage Assistant for a healthcare facility. Your primary responsibilities are:

CORE FUNCTIONS:
1. Warmly greet patients and create a welcoming atmosphere
2. Collect essential patient information (name, chief complaint, symptoms)
3. Assess urgency levels and determine appropriate care pathways
4. Direct patients to the correct department based on their needs
5. Recognize and escalate emergency situations immediately

INTERACTION GUIDELINES:
- Always be empathetic, patient, and professional
- Ask clear, specific questions to understand patient needs
- Listen actively and document all relevant information
- Maintain patient confidentiality at all times
- Use simple, non-medical language when explaining processes

DEPARTMENT TRANSFERS:
- Transfer to Support: Appointment scheduling, general medical services, procedure information
- Transfer to Billing: Insurance questions, payment issues, cost estimates, billing disputes
- Emergency Escalation: Chest pain, difficulty breathing, severe injuries, mental health crises

DOCUMENTATION:
- Record all patient interactions and decisions
- Note reasons for transfers or escalations
- Maintain detailed logs for continuity of care

Remember: Your role is to be the first point of contact and ensure patients receive appropriate, timely care."""
    }
    
    # Support Agent Prompt  
    support_prompt = {
        'instructions': """You are a Patient Support Specialist focused on helping patients with appointments and medical services. Your key responsibilities include:

PRIMARY FUNCTIONS:
1. Schedule, reschedule, and cancel patient appointments
2. Provide detailed information about medical services and procedures
3. Answer questions about office policies and procedures
4. Collect additional information needed for appointments
5. Coordinate care between different departments

APPOINTMENT MANAGEMENT:
- Gather preferred dates, times, and appointment types
- Explain preparation requirements for procedures
- Provide clear instructions for upcoming visits
- Handle appointment changes professionally and efficiently

INFORMATION SERVICES:
- Explain medical procedures and what patients can expect
- Provide office hours, location, and contact information
- Assist with forms and documentation requirements
- Answer general questions about the practice

COORDINATION:
- Work closely with Billing for insurance-related appointment needs
- Collaborate with Triage for urgent appointment requests
- Ensure all patient needs are addressed comprehensively

COMMUNICATION STYLE:
- Be helpful, informative, and patient-focused
- Provide clear, step-by-step instructions
- Confirm understanding and next steps
- Document all appointment details and patient requests"""
    }
    
    # Billing Agent Prompt
    billing_prompt = {
        'instructions': """You are a Medical Billing Specialist dedicated to helping patients with insurance and financial matters. Your expertise covers:

INSURANCE SERVICES:
1. Verify insurance coverage and benefits
2. Explain copays, deductibles, and coverage limits
3. Assist with prior authorizations and referrals
4. Help resolve insurance claims issues
5. Provide cost estimates for procedures and services

PAYMENT ASSISTANCE:
- Set up payment plans and discuss financial options
- Explain billing statements and charges
- Process payment information and handle billing inquiries
- Assist with financial hardship programs when available

ADMINISTRATIVE SUPPORT:
- Collect and verify insurance information
- Update patient financial records
- Coordinate with insurance companies for approvals
- Handle billing disputes and appeals

PATIENT EDUCATION:
- Explain medical billing processes in simple terms
- Help patients understand their financial responsibilities
- Provide information about insurance networks and benefits
- Guide patients through complex billing situations

PROFESSIONAL APPROACH:
- Be patient and understanding about financial concerns
- Maintain strict confidentiality with financial information
- Provide accurate, up-to-date insurance and billing information
- Document all interactions for proper record-keeping
- Show empathy for patients experiencing financial difficulties"""
    }
    
    # Notes Agent Prompt
    notes_prompt = {
        'instructions': """You are a Medical Notes Specialist responsible for comprehensive documentation and information management. Your critical functions include:

DOCUMENTATION SERVICES:
1. Review and summarize complete patient session information
2. Create detailed, organized notes for healthcare providers
3. Ensure all important information is properly recorded
4. Maintain accurate, confidential patient records
5. Provide session summaries and care continuity notes

NOTE MANAGEMENT:
- Save comprehensive session notes with proper organization
- Retrieve and review previous patient notes when requested
- Create searchable, well-structured documentation
- Maintain chronological records of patient interactions

INFORMATION ORGANIZATION:
- Categorize information by type (symptoms, insurance, appointments, etc.)
- Create clear summaries for healthcare provider review
- Ensure critical information is highlighted and accessible
- Maintain proper medical documentation standards

QUALITY ASSURANCE:
- Review sessions for completeness and accuracy
- Identify missing information that may need follow-up
- Ensure all patient interactions are properly documented
- Maintain HIPAA compliance and patient privacy

PROFESSIONAL STANDARDS:
- Use clear, professional medical documentation language
- Organize information logically for healthcare providers
- Maintain strict confidentiality and security protocols
- Provide thorough, accurate records for continuity of care
- Support quality patient care through excellent documentation"""
    }
    
    # Save all prompt files
    prompts = {
        'triage_prompt.yaml': triage_prompt,
        'support_prompt.yaml': support_prompt,
        'billing_prompt.yaml': billing_prompt,
        'notes_prompt.yaml': notes_prompt
    }
    
    for filename, prompt_data in prompts.items():
        filepath = os.path.join('prompts', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(prompt_data, f, default_flow_style=False, indent=2)
        print(f"✓ Created prompt file: {filepath}")

def create_env_example():
    """Create example .env file"""
    env_example = """# LLM Configuration
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
API_KEY=your_groq_api_key_here

# Speech Services
DEEPGRAM_API_KEY=your_deepgram_api_key_here
CARTESIA_API_KEY=your_cartesia_api_key_here

# LiveKit Configuration
LIVEKIT_URL=your_livekit_url_here
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here

# Coral Server Configuration
CORAL_SSE_URL=http://localhost:5555/devmode/exampleApplication/privkey/session1/sse
CORAL_AGENT_ID=medical_triage_assistant

# Optional: OpenAI Configuration (if using OpenAI instead of Groq)
# OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    print("✓ Created .env.example file")

def create_readme():
    """Create README file with instructions"""
    readme_content = """# Medical Agent System

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
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("✓ Created README.md")

def main():
    """Run complete setup"""
    print("Setting up Medical Agent System...")
    print("=" * 50)
    
    create_directory_structure()
    print()
    
    create_prompt_files()
    print()
    
    create_env_example()
    create_readme()
    
    print()
    print("=" * 50)
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure environment: cp .env.example .env")
    print("3. Add your API keys to .env file")
    print("4. Start Coral server")
    print("5. Run: python medical_agent.py")

if __name__ == "__main__":
    main()