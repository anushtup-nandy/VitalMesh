#!/usr/bin/env python3

import logging
import os
import asyncio
import urllib.parse
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path
import sys
import yaml

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import cartesia, deepgram, openai, groq, silero
from livekit.agents import mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medical-agent")

# Load environment variables
load_dotenv()

def create_directory_structure():
    """Create necessary directories"""
    Path("patient_notes").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

def get_patient_file_path(patient_identifier: str) -> str:
    """Get consistent file path for a patient"""
    # Sanitize filename and ensure consistency
    safe_name = "".join(c for c in patient_identifier.lower() if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    return f"patient_notes/{safe_name}.yaml"

def save_patient_notes(notes_data: Dict[str, Any], patient_identifier: str) -> str:
    """Save or update patient notes to a single file per patient"""
    filepath = get_patient_file_path(patient_identifier)
    
    existing_data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                existing_data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading existing notes: {e}")
    
    # Merge sessions - keep history
    if 'sessions' not in existing_data:
        existing_data['sessions'] = []
    
    # Add current session with timestamp
    session_data = notes_data.copy()
    session_data['session_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
    existing_data['sessions'].append(session_data)
    
    # Update patient metadata
    existing_data.update({
        'patient_name': notes_data.get('patient_name'),
        'patient_id': notes_data.get('patient_id'),
        'last_updated': datetime.now().isoformat(),
        'total_sessions': len(existing_data['sessions'])
    })
    
    try:
        with open(filepath, 'w') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Patient notes saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving notes: {e}")
        raise

def load_patient_notes(patient_identifier: str) -> Optional[Dict[str, Any]]:
    """Load patient notes from file"""
    filepath = get_patient_file_path(patient_identifier)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading patient notes: {e}")
        return None

def list_patient_notes() -> list:
    """List available patient note files"""
    notes_dir = Path("patient_notes")
    if not notes_dir.exists():
        return []
    
    files = []
    for file_path in notes_dir.glob("*.yaml"):
        try:
            stat = file_path.stat()
            files.append({
                'filename': file_path.name,
                'path': str(file_path),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

def get_llm_instance():
    """Get LLM instance based on environment configuration"""
    llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
    llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    api_key = os.getenv("API_KEY")
    
    if llm_provider == "openai":
        return openai.LLM(model=llm_model, api_key=api_key)
    elif llm_provider == "groq":
        return groq.LLM(model=llm_model, api_key=api_key)
    else:
        logger.warning(f"Unsupported LLM provider: {llm_provider}. Falling back to Groq.")
        return groq.LLM(model=llm_model, api_key=api_key)

@dataclass
class PatientSession:
    """Stores patient data throughout the session"""
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: list = field(default_factory=list)
    appointment_type: Optional[str] = None
    insurance_info: Optional[str] = None
    billing_questions: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    current_agent: Optional[str] = None
    session_start: datetime = field(default_factory=datetime.now)
    auto_save_enabled: bool = True
    conversation_ended: bool = False

    def add_note(self, note: str, agent_type: str = "system"):
        """Add a note to the patient session"""
        note_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_type,
            "content": note
        }
        self.notes.append(note_entry)
        logger.info(f"Added note: {note_entry}")

    def get_patient_identifier(self) -> str:
        """Get consistent patient identifier for file naming"""
        if self.patient_name:
            return self.patient_name.strip()
        elif self.patient_id:
            return self.patient_id.strip()
        else:
            return f"unknown_patient_{self.session_start.strftime('%Y%m%d_%H%M%S')}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving"""
        return {
            "patient_name": self.patient_name,
            "patient_id": self.patient_id,
            "chief_complaint": self.chief_complaint,
            "symptoms": self.symptoms,
            "appointment_type": self.appointment_type,
            "insurance_info": self.insurance_info,
            "billing_questions": self.billing_questions,
            "notes": self.notes,
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat()
        }

    def auto_save_notes(self):
        """Automatically save notes if enabled and there's data"""
        if self.auto_save_enabled and (self.notes or self.chief_complaint):
            try:
                patient_identifier = self.get_patient_identifier()
                filename = save_patient_notes(self.to_dict(), patient_identifier)
                logger.info(f"Auto-saved session notes to {filename}")
                return filename
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
                return None
        return None

@dataclass 
class MedicalAgentData:
    """Shared data across all medical agents"""
    patient_session: PatientSession = field(default_factory=PatientSession)
    agents: Dict[str, Agent] = field(default_factory=dict)
    previous_agent: Optional[Agent] = None
    ctx: Optional[JobContext] = None

RunContext_T = RunContext[MedicalAgentData]

class BaseMedicalAgent(Agent):
    """Base class for all medical agents with common functionality"""
    
    def __init__(self, agent_name: str, instructions: str):
        super().__init__(
            instructions=instructions,
            stt=deepgram.STT(),
            llm=get_llm_instance(),
            tts=cartesia.TTS(),
            vad=silero.VAD.load()
        )
        self.agent_name = agent_name

    def _detect_goodbye_intent(self, message: str) -> bool:
        """Detect if user wants to end conversation"""
        goodbye_phrases = [
            "goodbye", "bye", "see you", "thanks bye", "that's all", 
            "end call", "hang up", "done", "finish", "exit", "quit",
            "thank you bye", "goodbye for now", "talk to you later",
            "i'm done", "that's it", "no more questions"
        ]
        message_lower = message.lower().strip()
        return any(phrase in message_lower for phrase in goodbye_phrases)

    async def on_enter(self) -> None:
        """Called when agent becomes active"""
        logger.info(f"Entering {self.agent_name}")
        
        userdata: MedicalAgentData = self.session.userdata
        
        # Check if conversation was ended
        if userdata.patient_session.conversation_ended:
            logger.info("Conversation already ended, not entering agent")
            return
            
        userdata.patient_session.current_agent = self.agent_name
        userdata.patient_session.add_note(f"Entered {self.agent_name}", self.agent_name)
        
        # Set room attributes for tracking
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes({
                "agent": self.agent_name,
                "patient_id": userdata.patient_session.patient_id or "unknown"
            })

        # Update chat context with previous conversation if exists
        chat_ctx = self.chat_ctx.copy()
        
        if userdata.previous_agent:
            # Transfer relevant context from previous agent
            items_copy = self._get_relevant_context(userdata.previous_agent.chat_ctx.items)
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in items_copy if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)

        # Add context about current patient session - but don't assume patient data
        session_context = self._build_session_context(userdata.patient_session)
        if session_context != "New patient session":
            chat_ctx.add_message(
                role="system", 
                content=f"You are the {self.agent_name}. Current patient session context: {session_context}"
            )
        else:
            chat_ctx.add_message(
                role="system", 
                content=f"You are the {self.agent_name}. This is a new patient session. Wait for patient information before making assumptions."
            )
        
        await self.update_chat_ctx(chat_ctx)
        
        # Only generate reply if conversation hasn't ended
        if not userdata.patient_session.conversation_ended:
            self.session.generate_reply()

    async def on_exit(self) -> None:
        """Called when agent is leaving - auto-save notes"""
        logger.info(f"Exiting {self.agent_name}")
        
        userdata: MedicalAgentData = self.session.userdata
        userdata.patient_session.add_note(f"Exited {self.agent_name}", self.agent_name)
        
        # Auto-save notes when exiting (only if not already ended)
        if not userdata.patient_session.conversation_ended:
            filename = userdata.patient_session.auto_save_notes()
            if filename:
                logger.info(f"Session notes auto-saved to {filename}")

    def _get_relevant_context(self, items: list, keep_last: int = 6) -> list:
        """Extract relevant context from previous agent conversation"""
        relevant_items = []
        for item in reversed(items[-keep_last:]):
            if item.type == "message" and item.role in ["user", "assistant"]:
                relevant_items.append(item)
        return list(reversed(relevant_items))

    def _build_session_context(self, session: PatientSession) -> str:
        """Build context string from patient session - don't make assumptions"""
        context_parts = []
        
        if session.patient_name:
            context_parts.append(f"Patient: {session.patient_name}")
        if session.chief_complaint:
            context_parts.append(f"Chief Complaint: {session.chief_complaint}")
        if session.symptoms:
            context_parts.append(f"Symptoms: {', '.join(session.symptoms)}")
        if session.appointment_type:
            context_parts.append(f"Appointment Type: {session.appointment_type}")
        if session.insurance_info:
            context_parts.append(f"Insurance: {session.insurance_info}")
        
        return " | ".join(context_parts) if context_parts else "New patient session"

    async def _transfer_to_agent(self, agent_name: str, context: RunContext_T, message: str = None) -> Agent:
        """Transfer to another agent while preserving session data"""
        userdata = context.userdata
        
        # Don't transfer if conversation ended
        if userdata.patient_session.conversation_ended:
            logger.info("Conversation ended, not transferring")
            return self
            
        current_agent = context.session.current_agent
        next_agent = userdata.agents[agent_name]
        
        # Save transfer reason in notes
        userdata.patient_session.add_note(
            f"Transferred from {self.agent_name} to {agent_name}" + 
            (f": {message}" if message else ""),
            self.agent_name
        )
        
        userdata.previous_agent = current_agent
        
        if message:
            await self.session.say(message)
        
        return next_agent
    
    @function_tool
    async def end_conversation(self, context: RunContext_T):
        """Gracefully terminate the session when the patient says goodbye."""
        userdata = context.userdata
        userdata.patient_session.conversation_ended = True

        # Save notes before closing
        filename = userdata.patient_session.auto_save_notes()
        if filename:
            logger.info(f"Final notes saved to {filename}")

        await self.session.say("Thank you for visiting us today. Take care and have a great day!")
        await asyncio.sleep(2)  # Let TTS finish
        
        logger.info("Ending conversation gracefully...")
        
        try:
            await self.session.close()
        except Exception as e:
            logger.error(f"Error closing session: {e}")
        
        # Exit the program
        logger.info("Exiting program...")
        sys.exit(0)

class TriageAgent(BaseMedicalAgent):
    """Initial triage agent for patient assessment"""
    
    def __init__(self):
        instructions = """
        You are a Medical Triage Assistant. Your role is to:
        1. Greet patients warmly and professionally 
        2. ASK for their name and reason for calling - DO NOT assume patient information
        3. Gather initial information: name, chief complaint, symptoms
        4. Determine urgency level and appropriate care pathway
        5. Direct patients to the correct department (support for appointments, billing for insurance/payments)
        6. Handle emergency situations by escalating appropriately
        7. Listen for goodbye/farewell intentions and call end_conversation when appropriate
        
        IMPORTANT RULES:
        - DO NOT assume any patient information (name, complaint, symptoms)
        - Always ASK before collecting information 
        - Wait for the patient to provide their details
        - Use collect_patient_info function only AFTER patient provides information
        - If patient says goodbye/bye/done/thanks bye, call end_conversation function
        
        Be empathetic, clear, and thorough in your assessment.
        """
        super().__init__("TriageAgent", instructions)

    async def on_user_speech_committed(self, message: str) -> None:
        """Check for goodbye intent in user speech"""
        if self._detect_goodbye_intent(message):
            logger.info(f"Detected goodbye intent: {message}")
            await self.end_conversation(self.session.ctx)

    @function_tool
    async def collect_patient_info(self, name: str, complaint: str, symptoms: str, context: RunContext_T):
        """Collect and store initial patient information - only when provided by patient"""
        userdata = context.userdata
        session = userdata.patient_session
        
        # Clean and validate inputs
        name = name.strip() if name else None
        complaint = complaint.strip() if complaint else None
        symptoms_list = [s.strip() for s in symptoms.split(",") if s.strip()] if symptoms else []
        
        if name:
            session.patient_name = name
        if complaint:
            session.chief_complaint = complaint
        if symptoms_list:
            session.symptoms = symptoms_list
        
        session.add_note(f"Patient information collected - Name: {name}, Complaint: {complaint}, Symptoms: {symptoms}", "triage")
        logger.info(f"Collected patient info: {name}, {complaint}")
        
        if name:
            await self.session.say(f"Thank you {name}. I've recorded your information. Let me help direct you to the appropriate department.")
        else:
            await self.session.say("Thank you. I've recorded your information. Let me help direct you to the appropriate department.")

    @function_tool 
    async def transfer_to_support(self, context: RunContext_T) -> Agent:
        """Transfer to patient support for appointments and general inquiries"""
        message = "I'll connect you with our Patient Support team who can help with scheduling and medical services."
        return await self._transfer_to_agent("support", context, message)

    @function_tool
    async def transfer_to_billing(self, context: RunContext_T) -> Agent:
        """Transfer to billing for insurance and payment questions"""
        message = "I'll transfer you to our Billing department who can assist with insurance and payment matters."
        return await self._transfer_to_agent("billing", context, message)

    @function_tool
    async def emergency_escalation(self, urgency_level: str, context: RunContext_T):
        """Handle emergency situations"""
        userdata = context.userdata
        userdata.patient_session.add_note(f"EMERGENCY ESCALATION: {urgency_level}", "triage")
        
        if urgency_level.lower() in ["high", "emergency", "urgent"]:
            await self.session.say("This appears to be an urgent medical situation. Please call 911 immediately or go to your nearest emergency room.")
        else:
            await self.session.say("Based on your symptoms, I recommend scheduling an appointment with your healthcare provider soon.")

class SupportAgent(BaseMedicalAgent):
    """Patient support agent for appointments and general inquiries"""
    
    def __init__(self):
        instructions = """
        You are a Patient Support Specialist. Your role is to:
        1. Help patients schedule, reschedule, or cancel appointments
        2. Provide information about medical services and procedures
        3. Answer general questions about the practice
        4. Collect additional information needed for appointments
        5. Coordinate with other departments as needed
        6. Listen for goodbye/farewell intentions and call end_conversation when appropriate
        
        Be helpful, informative, and patient-focused.
        Document all appointment details and patient requests.
        If patient says goodbye/bye/done/thanks bye, call end_conversation function.
        """
        super().__init__("SupportAgent", instructions)

    async def on_user_speech_committed(self, message: str) -> None:
        """Check for goodbye intent in user speech"""
        if self._detect_goodbye_intent(message):
            logger.info(f"Detected goodbye intent: {message}")
            await self.end_conversation(self.session.ctx)

    @function_tool
    async def schedule_appointment(self, appointment_type: str, preferred_date: str, preferred_time: str, context: RunContext_T):
        """Schedule an appointment for the patient"""
        userdata = context.userdata
        session = userdata.patient_session
        
        session.appointment_type = appointment_type
        session.add_note(f"Appointment requested: {appointment_type} on {preferred_date} at {preferred_time}", "support")
        
        await self.session.say(f"I've noted your request for a {appointment_type} appointment on {preferred_date} at {preferred_time}. Our scheduling team will contact you to confirm.")

    @function_tool
    async def transfer_to_billing(self, context: RunContext_T) -> Agent:
        """Transfer to billing for insurance questions"""
        message = "Let me connect you with our Billing team for insurance and payment assistance."
        return await self._transfer_to_agent("billing", context, message)

    @function_tool  
    async def transfer_to_triage(self, context: RunContext_T) -> Agent:
        """Transfer back to triage if medical assessment needed"""
        message = "Let me connect you back with our Triage team for medical assessment."
        return await self._transfer_to_agent("triage", context, message)

class BillingAgent(BaseMedicalAgent):
    """Billing agent for insurance and payment inquiries"""
    
    def __init__(self):
        instructions = """
        You are a Medical Billing Specialist. Your role is to:
        1. Answer questions about insurance coverage and benefits
        2. Help with payment plans and billing inquiries
        3. Explain medical billing processes and codes
        4. Assist with insurance authorizations and claims
        5. Provide cost estimates for procedures
        6. Listen for goodbye/farewell intentions and call end_conversation when appropriate
        
        Be knowledgeable about billing processes while remaining patient and helpful.
        Document all billing-related questions and resolutions.
        If patient says goodbye/bye/done/thanks bye, call end_conversation function.
        """
        super().__init__("BillingAgent", instructions)

    async def on_user_speech_committed(self, message: str) -> None:
        """Check for goodbye intent in user speech"""
        if self._detect_goodbye_intent(message):
            logger.info(f"Detected goodbye intent: {message}")
            await self.end_conversation(self.session.ctx)

    @function_tool
    async def collect_insurance_info(self, insurance_provider: str, member_id: str, group_number: str, context: RunContext_T):
        """Collect patient insurance information"""
        userdata = context.userdata
        session = userdata.patient_session
        
        session.insurance_info = f"Provider: {insurance_provider}, Member ID: {member_id}, Group: {group_number}"
        session.add_note(f"Insurance information collected: {session.insurance_info}", "billing")
        
        await self.session.say("Thank you. I've recorded your insurance information and will verify your coverage.")

    @function_tool
    async def add_billing_question(self, question: str, context: RunContext_T):
        """Log billing questions for follow-up"""
        userdata = context.userdata
        session = userdata.patient_session
        
        session.billing_questions.append(question)
        session.add_note(f"Billing question: {question}", "billing")
        
        await self.session.say("I've noted your question. Our billing team will follow up with detailed information.")

    @function_tool
    async def transfer_to_support(self, context: RunContext_T) -> Agent:
        """Transfer to support for appointment scheduling"""
        message = "Let me connect you with Patient Support to help with scheduling."
        return await self._transfer_to_agent("support", context, message)

    @function_tool
    async def transfer_to_triage(self, context: RunContext_T) -> Agent:
        """Transfer to triage for medical questions"""
        message = "Let me connect you with our Triage team for medical concerns."
        return await self._transfer_to_agent("triage", context, message)

async def entrypoint(ctx: JobContext):
    """Main entry point for the medical agent system"""
    await ctx.connect()
    logger.info("Medical Agent System starting...")

    # Create directories first
    create_directory_structure()

    # Initialize agents
    triage_agent = TriageAgent()
    support_agent = SupportAgent()
    billing_agent = BillingAgent()

    # Create shared user data
    userdata = MedicalAgentData(ctx=ctx)
    userdata.agents.update({
        "triage": triage_agent,
        "support": support_agent,
        "billing": billing_agent
    })

    # Temporarily disable MCP connection until Coral is working properly
    session = AgentSession[MedicalAgentData](userdata=userdata)

    logger.info("Starting session with Triage Agent...")
    
    try:
        await session.start(
            agent=triage_agent,  # Start with triage
            room=ctx.room,
        )
    except Exception as e:
        logger.error(f"Session error: {e}")
    finally:
        # Ensure notes are saved when session ends
        logger.info("Session ending - performing final save...")
        if not userdata.patient_session.conversation_ended:
            filename = userdata.patient_session.auto_save_notes()
            if filename:
                logger.info(f"Final session notes saved to {filename}")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))