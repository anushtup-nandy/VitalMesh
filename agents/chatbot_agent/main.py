#!/usr/bin/env python3
# <project-root>/agents/chatbot_agent/main.py
import os
import yaml
from groq import Groq
from pathlib import Path
from datetime import datetime

class MedicalChatbot:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("API_KEY"))
        self.llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        self.ehr_dir = Path(os.getenv("EHR_OUTPUT_DIR", "../ehr_agent/ehr_outputs"))
        
        # Load all EHR data
        self.patient_data = self.load_all_ehr_data()
        
        # REALLY REALLY good system prompt
        self.system_prompt = """You are Dr. VitalMesh, an exceptional AI medical assistant with access to comprehensive Electronic Health Records. You are:

🩺 **MEDICAL EXPERTISE**: A board-certified physician with deep knowledge across all medical specialties. You understand complex medical conditions, treatments, diagnostics, and patient care protocols.

🧠 **ANALYTICAL MIND**: You analyze patient data with precision, identifying patterns, correlations, and potential concerns that others might miss. You think systematically and consider differential diagnoses.

💬 **CONVERSATIONAL EXCELLENCE**: You communicate complex medical information in clear, understandable language. You adapt your tone based on who you're speaking with - technical with healthcare providers, compassionate with patients/families.

📊 **DATA MASTERY**: You have instant access to all patient EHR data and can:
- Quickly retrieve specific patient information
- Compare symptoms across patients
- Track patient progress over time  
- Identify trends and risk factors
- Provide evidence-based recommendations

🎯 **CORE CAPABILITIES**:
- Answer ANY question about your patients with specific, detailed responses
- Provide clinical insights, assessments, and recommendations
- Explain medical conditions, treatments, and procedures
- Compare patient cases and identify patterns
- Offer second opinions and differential diagnoses
- Suggest follow-up care and monitoring plans
- Flag urgent or concerning findings

🔒 **PROFESSIONAL STANDARDS**: You maintain strict medical confidentiality, use proper medical terminology when appropriate, and always include necessary disclaimers about seeking direct medical care.

📝 **COMMUNICATION STYLE**:
- Be conversational yet professional
- Use specific patient data when answering questions
- Provide context and reasoning for your assessments  
- Offer actionable insights and recommendations
- Ask clarifying questions when needed
- Be empathetic and supportive

When responding:
1. **Reference specific patient data** when relevant (use patient IDs)
2. **Provide detailed medical analysis** with clinical reasoning
3. **Offer practical next steps** and recommendations
4. **Explain complex concepts** in understandable terms
5. **Include appropriate medical disclaimers** when giving clinical advice

You are not just answering questions - you are providing expert medical consultation based on comprehensive patient records. Be thorough, insightful, and genuinely helpful."""

    def load_all_ehr_data(self):
        """Load all EHR files into memory"""
        patient_data = {}
        
        if not self.ehr_dir.exists():
            print(f"⚠️  EHR directory not found: {self.ehr_dir}")
            return patient_data
            
        ehr_files = list(self.ehr_dir.glob("*_comprehensive_ehr.yaml"))
        print(f"📋 Loading {len(ehr_files)} EHR files...")
        
        for ehr_file in ehr_files:
            try:
                with open(ehr_file, 'r') as f:
                    patient_id = ehr_file.stem.replace('_comprehensive_ehr', '')
                    patient_data[patient_id] = {
                        'data': yaml.safe_load(f),
                        'file_path': str(ehr_file),
                        'last_updated': datetime.fromtimestamp(ehr_file.stat().st_mtime)
                    }
            except Exception as e:
                print(f"❌ Error loading {ehr_file}: {e}")
        
        print(f"✅ Loaded EHR data for {len(patient_data)} patients")
        return patient_data

    def refresh_data(self):
        """Refresh EHR data from files"""
        print("🔄 Refreshing patient data...")
        self.patient_data = self.load_all_ehr_data()

    def get_context_for_query(self, query):
        """Get relevant patient context based on the query"""
        query_lower = query.lower()
        relevant_patients = []
        
        # If query mentions specific patient ID
        for patient_id in self.patient_data.keys():
            if patient_id.lower() in query_lower:
                relevant_patients = [patient_id]
                break
        
        # If no specific patient mentioned, find relevant ones based on keywords
        if not relevant_patients:
            for patient_id, patient_info in self.patient_data.items():
                patient_str = yaml.dump(patient_info['data'], default_flow_style=False).lower()
                if any(word in patient_str for word in query_lower.split() if len(word) > 3):
                    relevant_patients.append(patient_id)
        
        # If still no matches, include all patients for general queries
        if not relevant_patients:
            relevant_patients = list(self.patient_data.keys())[:3]  # Limit to 3 for context size
        
        # Build context string
        context = "\n=== PATIENT EHR DATABASE ===\n"
        for patient_id in relevant_patients:
            if patient_id in self.patient_data:
                context += f"\n📋 PATIENT {patient_id.upper()}:\n"
                context += yaml.dump(self.patient_data[patient_id]['data'], default_flow_style=False)
                context += f"\nLast Updated: {self.patient_data[patient_id]['last_updated']}\n"
                context += "-" * 50 + "\n"
        
        return context

    def chat(self, user_input):
        """Main chat function"""
        if user_input.lower().strip() in ['quit', 'exit', 'bye']:
            return "👋 Goodbye! Stay healthy!"
        
        if user_input.lower().strip() == 'refresh':
            self.refresh_data()
            return f"🔄 Data refreshed! Now tracking {len(self.patient_data)} patients."
        
        # Get relevant context
        context = self.get_context_for_query(user_input)
        
        # Create the prompt
        full_prompt = f"{context}\n\n🗣️ QUERY: {user_input}\n\nPlease provide a detailed medical response based on the available patient data."
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ Error: {e}\n\nPlease try again or check your API connection."

    def run_interactive(self):
        """Run interactive chat session"""
        print("🏥 Dr. VitalMesh Medical Chatbot")
        print("=" * 50)
        print(f"📊 Loaded data for {len(self.patient_data)} patients")
        print("💬 Ask me anything about your patients!")
        print("🔄 Type 'refresh' to reload patient data")
        print("👋 Type 'quit' to exit")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n🗣️  You: ").strip()
                if not user_input:
                    continue
                    
                print("\n🩺 Dr. VitalMesh:")
                response = self.chat(user_input)
                print(response)
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    chatbot = MedicalChatbot()
    chatbot.run_interactive()