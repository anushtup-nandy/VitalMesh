#!/usr/bin/env python3

import logging
import os
import asyncio
import urllib.parse
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import cartesia, deepgram, openai, groq, silero
from livekit.agents import mcp

# Import our custom utilities
from utils import load_prompt, save_patient_notes, load_patient_notes, list_patient_notes, create_directory_structure

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medical-agent")

# Load environment variables
load_dotenv()

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

    def add_note(self, note: str, agent_type: str = "system"):
        """Add a note to the patient session"""
        note_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_type,
            "content": note
        }
        self.notes.append(note_entry)
        logger.info(f"Added note: {note_entry}")

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
                patient_identifier = self.patient_name or self.patient_id or "unknown_patient"
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

    async def on_enter(self) -> None:
        """Called when agent becomes active"""
        logger.info(f"Entering {self.agent_name}")
        
        userdata: MedicalAgentData = self.session.userdata
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

        # Add context about current patient session
        session_context = self._build_session_context(userdata.patient_session)
        chat_ctx.add_message(
            role="system", 
            content=f"You are the {self.agent_name}. Current patient session context: {session_context}"
        )
        
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply()

    async def on_exit(self) -> None:
        """Called when agent is leaving - auto-save notes"""
        logger.info(f"Exiting {self.agent_name}")
        
        userdata: MedicalAgentData = self.session.userdata
        userdata.patient_session.add_note(f"Exited {self.agent_name}", self.agent_name)
        
        # Auto-save notes when exiting
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
        """Build context string from patient session"""
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

        # Save notes before closing
        filename = userdata.patient_session.auto_save_notes()
        if filename:
            logger.info(f"Final notes saved to {filename}")

        await self.session.say("Thank you for visiting us. Take care!")
        await asyncio.sleep(1)  # let TTS finish

        logger.info("Closing AgentSession...")
        await self.session.close()

class TriageAgent(BaseMedicalAgent):
    """Initial triage agent for patient assessment"""
    
    def __init__(self):
        instructions = """
        You are a Medical Triage Assistant. Your role is to:
        1. Greet patients warmly and professionally
        2. Gather initial information: name, chief complaint, symptoms
        3. Determine urgency level and appropriate care pathway
        4. Direct patients to the correct department (support for appointments, billing for insurance/payments)
        5. Handle emergency situations by escalating appropriately
        
        Always be empathetic, clear, and thorough in your assessment.
        Ask follow-up questions to understand the patient's needs.
        Document all relevant information for the next agent.
        
        IMPORTANT: Always collect patient information using the collect_patient_info function.
        """
        super().__init__("TriageAgent", instructions)

    @function_tool
    async def collect_patient_info(self, name: str, complaint: str, symptoms: str, context: RunContext_T):
        """Collect and store initial patient information"""
        userdata = context.userdata
        session = userdata.patient_session
        
        session.patient_name = name
        session.chief_complaint = complaint
        session.symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]
        
        session.add_note(f"Initial triage completed. Chief complaint: {complaint}", "triage")
        logger.info(f"Collected patient info: {name}, {complaint}")
        
        await self.session.say(f"Thank you {name}. I've recorded your information. Let me direct you to the appropriate department.")

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

    @function_tool
    async def save_notes_now(self, context: RunContext_T):
        """Manually save session notes"""
        userdata = context.userdata
        filename = userdata.patient_session.auto_save_notes()
        if filename:
            await self.session.say(f"I've saved your session information for our medical team.")
        else:
            await self.session.say("I'll make sure your information is documented.")

# ... (SupportAgent, BillingAgent, NotesAgent classes remain the same as original)

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
        
        Be helpful, informative, and patient-focused.
        Document all appointment details and patient requests.
        """
        super().__init__("SupportAgent", instructions)

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
        
        Be knowledgeable about billing processes while remaining patient and helpful.
        Document all billing-related questions and resolutions.
        """
        super().__init__("BillingAgent", instructions)

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

class NotesAgent(BaseMedicalAgent):
    """Specialized agent for managing patient notes and documentation"""
    
    def __init__(self):
        instructions = """
        You are a Medical Notes Specialist. Your role is to:
        1. Review and summarize patient session information
        2. Save comprehensive patient notes to files
        3. Retrieve previous patient notes when requested
        4. Ensure all important information is documented
        5. Provide summaries for healthcare providers
        
        Be thorough, accurate, and maintain patient confidentiality.
        Organize information clearly for medical professionals.
        """
        super().__init__("NotesAgent", instructions)

    @function_tool
    async def save_session_notes(self, context: RunContext_T) -> str:
        """Save the current session notes to a file"""
        userdata = context.userdata
        session = userdata.patient_session
        
        # Prepare notes data
        notes_data = session.to_dict()
        
        # Save to file
        patient_identifier = session.patient_name or session.patient_id or "unknown_patient"
        filename = save_patient_notes(notes_data, patient_identifier)
        
        session.add_note(f"Session notes saved to {filename}", "notes")
        await self.session.say(f"I've saved all session notes to {filename}. The information has been documented for your healthcare team.")
        
        return filename

    @function_tool
    async def load_previous_notes(self, patient_name: str, context: RunContext_T):
        """Load previous patient notes"""
        userdata = context.userdata
        
        # List available notes files
        available_notes = list_patient_notes()
        matching_files = [note for note in available_notes if patient_name.lower() in note['filename'].lower()]
        
        if matching_files:
            latest_file = matching_files[0]  # Most recent
            notes_data = load_patient_notes(latest_file['filename'])
            
            if notes_data:
                # Add summary to current session
                userdata.patient_session.add_note(f"Loaded previous notes from {latest_file['filename']}", "notes")
                await self.session.say(f"I found previous notes for {patient_name} from {latest_file['created'].strftime('%Y-%m-%d')}. The information has been added to the current session context.")
            else:
                await self.session.say(f"I found a notes file but couldn't load the data. Please check the file format.")
        else:
            await self.session.say(f"No previous notes found for {patient_name}.")

    @function_tool
    async def transfer_to_triage(self, context: RunContext_T) -> Agent:
        """Transfer back to triage"""
        message = "Returning you to our Triage team."
        return await self._transfer_to_agent("triage", context, message)

async def entrypoint(ctx: JobContext):
    """Main entry point for the medical agent system"""
    await ctx.connect()
    logger.info("Medical Agent System starting...")

    #Configure MCP Server connection for Coral
    # base_url = os.getenv("CORAL_SSE_URL", "http://localhost:5555/devmode/exampleApplication/privkey/session1/sse")
    base_url = os.getenv("CORAL_SSE_URL", "http://localhost:5555")
    params = {
        "agentId": os.getenv("CORAL_AGENT_ID", "medical_triage_assistant"),
        "agentDescription": "Multi-agent medical office system for triage, support, billing, and documentation."
    }
    query_string = urllib.parse.urlencode(params)
    mcp_server_url = f"{base_url}?{query_string}"
    
    logger.info(f"Connecting to Coral MCP Server: {mcp_server_url}")

    # Create directories first
    create_directory_structure()

    # Initialize agents
    triage_agent = TriageAgent()
    support_agent = SupportAgent()
    billing_agent = BillingAgent()  
    notes_agent = NotesAgent()

    # Create shared user data
    userdata = MedicalAgentData(ctx=ctx)
    userdata.agents.update({
        "triage": triage_agent,
        "support": support_agent,
        "billing": billing_agent,
        "notes": notes_agent
    })

    # Create session WITHOUT MCP server for now (until Coral is fixed)
    session = AgentSession[MedicalAgentData](
        userdata=userdata,
        # Temporarily disabled until MCP server is working
        mcp_servers=[
            mcp.MCPServerHTTP(
                url=mcp_server_url,
                timeout=10,
                client_session_timeout_seconds=30,
            ),
        ]
    )

    logger.info("Starting session with Triage Agent...")
    
    try:
        await session.start(
            agent=triage_agent,  # Start with triage
            room=ctx.room,
        )
    finally:
        # Ensure notes are saved when session ends
        logger.info("Session ending - performing final save...")
        filename = userdata.patient_session.auto_save_notes()
        if filename:
            logger.info(f"Final session notes saved to {filename}")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))