#!/usr/bin/env python3

import asyncio
import json
import os
import yaml
from datetime import datetime
from groq import Groq
import requests
from pathlib import Path
import random

class EHRAgent:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq")
        self.llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        self.api_key = os.getenv("API_KEY")
        self.coral_sse_url = os.getenv("CORAL_SSE_URL", "http://localhost:5555")
        self.agent_id = os.getenv("CORAL_AGENT_ID", "ehr_agent")
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./ehr_outputs"))
        self.patient_notes_dir = Path("../medical_agent/patient_notes/")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Groq client
        if self.llm_provider == "groq":
            self.client = Groq(api_key=self.api_key)
        
        # Store processed EHR data for answering questions
        self.ehr_database = {}
        
        # System prompt for medical EHR processing
        self.system_prompt = """You are a professional Electronic Health Records (EHR) Assistant with extensive medical knowledge. Your primary responsibilities are:

1. **Process patient data** from medical triage sessions and convert it into comprehensive, structured YAML files
2. **Provide medical insights** and professional analysis of patient conditions
3. **Generate detailed clinical documentation** that would be useful for healthcare providers
4. **Maintain HIPAA compliance** and medical confidentiality standards

When processing patient data, you must:
- Extract all relevant medical information (symptoms, vitals, history, etc.)
- Categorize information by medical relevance and urgency
- Provide clinical assessments and differential diagnoses when appropriate
- Format everything in a clean, structured YAML format suitable for frontend rendering
- Include timestamps, severity levels, and follow-up recommendations

Your YAML output should include these sections:
- patient_info (demographics, contact, patient ID number (if no patient ID number on file, create one))
- chief_complaint (primary reason for visit)
- symptoms (detailed symptom analysis)
- vitals (if available)
- medical_history (relevant past medical history)
- assessment (your professional medical assessment)
- recommendations (next steps, follow-up care)
- urgency_level (low/medium/high/critical)
- generated_at (timestamp)

Always respond professionally as a medical expert would, but remember to include appropriate disclaimers about seeking professional medical care."""

    def load_patient_notes(self) -> list:
        """Load all patient notes from medical agent directory"""
        patient_files = []
        if not self.patient_notes_dir.exists():
            print(f"⚠️  Patient notes directory not found: {self.patient_notes_dir}")
            return patient_files
            
        for yaml_file in self.patient_notes_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    patient_data = yaml.safe_load(f)
                    patient_files.append({
                        'filename': yaml_file.name,
                        'filepath': str(yaml_file),
                        'data': patient_data,
                        'last_modified': yaml_file.stat().st_mtime
                    })
            except Exception as e:
                print(f"❌ Error loading {yaml_file}: {e}")
                
        print(f"📋 Loaded {len(patient_files)} patient note files")
        return patient_files

    def process_patient_notes(self):
        """Process all patient notes and create comprehensive EHR files"""
        patient_files = self.load_patient_notes()
        
        for patient_file in patient_files:
            try:
                # Check if we already processed this file (based on modification time)
                patient_id = patient_file['filename'].replace('.yaml', '')
                ehr_file = self.output_dir / f"{patient_id}_comprehensive_ehr.yaml"
                
                if ehr_file.exists():
                    ehr_mod_time = ehr_file.stat().st_mtime
                    if patient_file['last_modified'] <= ehr_mod_time:
                        print(f"✅ {patient_id} already processed and up to date")
                        # Load existing EHR into database
                        with open(ehr_file, 'r') as f:
                            self.ehr_database[patient_id] = yaml.safe_load(f)
                        continue
                
                print(f"🏥 Processing patient notes for: {patient_id}")
                
                # Convert patient data to string for LLM processing
                patient_data_str = yaml.dump(patient_file['data'], default_flow_style=False)
                
                # Generate comprehensive EHR
                comprehensive_ehr = self.process_with_llm(patient_data_str)
                
                if comprehensive_ehr:
                    # Save comprehensive EHR
                    filepath = self.save_ehr_yaml(comprehensive_ehr, f"{patient_id}_comprehensive")
                    
                    if filepath:
                        # Parse and store in database for quick access
                        try:
                            ehr_data = yaml.safe_load(comprehensive_ehr)
                            self.ehr_database[patient_id] = ehr_data
                            print(f"✅ Processed and stored EHR for {patient_id}")
                        except yaml.YAMLError as e:
                            print(f"❌ Error parsing generated YAML for {patient_id}: {e}")
                else:
                    print(f"❌ Failed to generate EHR for {patient_id}")
                    
            except Exception as e:
                print(f"❌ Error processing {patient_file['filename']}: {e}")

    def watch_for_new_notes(self):
        """Check for new or updated patient notes"""
        if not hasattr(self, '_last_check_time'):
            self._last_check_time = datetime.now().timestamp()
            
        current_time = datetime.now().timestamp()
        new_files = []
        
        if self.patient_notes_dir.exists():
            for yaml_file in self.patient_notes_dir.glob("*.yaml"):
                if yaml_file.stat().st_mtime > self._last_check_time:
                    new_files.append(yaml_file)
                    
        if new_files:
            print(f"📥 Found {len(new_files)} new/updated patient notes")
            self.process_patient_notes()
            
        self._last_check_time = current_time

    def search_ehr_database(self, query: str) -> dict:
        """Search through EHR database for relevant information"""
        results = {}
        query_lower = query.lower()
        
        for patient_id, ehr_data in self.ehr_database.items():
            # Search through EHR data for relevant information
            matches = []
            ehr_str = yaml.dump(ehr_data, default_flow_style=False).lower()
            
            if any(term in ehr_str for term in query_lower.split()):
                results[patient_id] = ehr_data
                
        return results

    async def connect_to_coral(self):
        """Connect to Coral server via SSE"""
        print(f"🌊 Connecting EHR Agent to Coral Server at {self.coral_sse_url}")
        # In a real implementation, this would establish SSE connection
        # For now, we'll simulate the connection
        return True

    def process_with_llm(self, patient_data: str) -> str:
        """Process patient data through LLM to generate EHR YAML"""
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Process this patient data and create a comprehensive EHR YAML file:\n\n{patient_data}"}
                ],
                temperature=0.1,  # Low temperature for consistent medical documentation
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error processing with LLM: {e}")
            return None

    def save_ehr_yaml(self, yaml_content: str, patient_id: str = None) -> str:
        """Save the generated EHR YAML to file"""
        if not patient_id:
            patient_id = f"{random.randint(100, 999)}"
        
        filename = f"{patient_id}.yaml"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                f.write(yaml_content)
            print(f"✅ EHR file saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Error saving EHR file: {e}")
            return None

    def validate_yaml(self, yaml_content: str) -> bool:
        """Validate that the generated content is proper YAML"""
        try:
            yaml.safe_load(yaml_content)
            return True
        except yaml.YAMLError:
            return False

    async def handle_message(self, message: dict):
        """Handle incoming messages from other agents via Coral"""
        try:
            message_type = message.get("type")
            content = message.get("content")
            sender = message.get("sender")
            
            print(f"📨 Received message from {sender}: {message_type}")
            
            if message_type == "patient_data":
                # Process patient data and generate EHR YAML
                print("🏥 Processing patient data for EHR generation...")
                
                ehr_yaml = self.process_with_llm(content)
                
                if ehr_yaml and self.validate_yaml(ehr_yaml):
                    # Save to file
                    patient_id = message.get("patient_id")
                    filepath = self.save_ehr_yaml(ehr_yaml, patient_id)
                    
                    # Send response back through Coral
                    response = {
                        "type": "ehr_generated",
                        "content": ehr_yaml,
                        "filepath": filepath,
                        "sender": self.agent_id,
                        "recipient": sender
                    }
                    await self.send_coral_message(response)
                    
                else:
                    print("❌ Failed to generate valid EHR YAML")
                    
            elif message_type == "medical_query":
                # Answer medical questions using EHR database
                print("🩺 Processing medical query with EHR database...")
                
                medical_response = self.answer_medical_question(content)
                
                response = {
                    "type": "medical_response",
                    "content": medical_response,
                    "sender": self.agent_id,
                    "recipient": sender
                }
                await self.send_coral_message(response)
                
        except Exception as e:
            print(f"❌ Error handling message: {e}")

    async def send_coral_message(self, message: dict):
        """Send message through Coral protocol"""
        try:
            # In a real implementation, this would use Coral's MCP protocol
            print(f"📤 Sending message via Coral: {message['type']}")
            # Simulate sending message
            pass
        except Exception as e:
            print(f"❌ Error sending Coral message: {e}")

    async def run(self):
        """Main agent loop"""
        print(f"🚀 Starting EHR Agent ({self.agent_id})")
        print(f"🔧 Using {self.llm_provider} with model {self.llm_model}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📋 Patient notes directory: {self.patient_notes_dir}")
        
        # Connect to Coral server
        await self.connect_to_coral()
        
        # Initial processing of existing patient notes
        print("🔄 Processing existing patient notes...")
        self.process_patient_notes()
        
        print("✅ EHR Agent is running and ready!")
        print("🔄 Monitoring for new patient notes and listening for queries...")
        
        # Main event loop
        try:
            while True:
                # Check for new patient notes every 30 seconds
                self.watch_for_new_notes()
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 EHR Agent shutting down...")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    agent = EHRAgent()
    asyncio.run(agent.run())