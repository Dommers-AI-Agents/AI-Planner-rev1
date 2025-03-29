import os
import logging
from typing import Dict, Any, Optional, List
import json

# Placeholder for actual communication APIs
# In a real implementation, you would import proper libraries:
# import twilio.rest
# from sendgrid import SendGridAPIClient
# from anthropic import Anthropic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommunicationHandler:
    """
    Handles all external communications with participants and organizers
    via SMS, email, and phone calls.
    """
    
    def __init__(self, 
                 sms_enabled: bool = True, 
                 email_enabled: bool = True, 
                 voice_enabled: bool = True,
                 api_key: Optional[str] = None):
        """Initialize the CommunicationHandler with configuration."""
        self.sms_enabled = sms_enabled
        self.email_enabled = email_enabled
        self.voice_enabled = voice_enabled
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        
        # Setup communication clients
        # self.twilio_client = twilio.rest.Client(account_sid, auth_token) 
        # self.email_client = SendGridAPIClient(sendgrid_api_key)
        # self.llm_client = Anthropic(api_key=self.api_key)
        
        logger.info("Communication Handler initialized")
        
    def initiate_contact(self, session_id: str, participant_id: str, 
                         participant_name: str, participant_contact: str,
                         organizer_name: str, event_name: str) -> None:
        """
        Initiates first contact with a participant to introduce the AI agent
        and ask for their preferred communication method.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            participant_name: Name of the participant
            participant_contact: Contact information (phone/email)
            organizer_name: Name of the event organizer
            event_name: Name of the event being planned
        """
        # Determine if contact is phone or email based on format
        contact_type = self._detect_contact_type(participant_contact)
        
        # Initial message template
        message = (
            f"Hi {participant_name}, {organizer_name} is planning {event_name} "
            f"and has asked me (an AI assistant) to help coordinate. "
            f"How would you prefer to answer a few questions about your preferences? "
            f"Reply with: 1 for text, 2 for email, or A3 for a phone call."
        )
        
        # Send via appropriate channel
        if contact_type == "phone" and self.sms_enabled:
            self._send_sms(participant_contact, message)
            logger.info(f"Sent initial SMS to {participant_name} for session {session_id}")
        elif contact_type == "email" and self.email_enabled:
            subject = f"Help Plan: {event_name} with {organizer_name}"
            self._send_email(participant_contact, subject, message)
            logger.info(f"Sent initial email to {participant_name} for session {session_id}")
        else:
            logger.warning(f"Could not initiate contact with {participant_name}: invalid contact info or method disabled")
    
    def _detect_contact_type(self, contact: str) -> str:
        """Determine if contact info is phone or email based on format."""
        if "@" in contact:
            return "email"
        else:
            # Basic assumption that non-email is phone
            return "phone"
    
    def _send_sms(self, to_number: str, message: str) -> None:
        """Send SMS message using Twilio or similar service."""
        # In a real implementation:
        # self.twilio_client.messages.create(
        #     body=message,
        #     from_=self.twilio_number,
        #     to=to_number
        # )
        logger.info(f"SMS would be sent to {to_number}: {message[:50]}...")
    
    def _send_email(self, to_email: str, subject: str, body: str) -> None:
        """Send email using SendGrid or similar service."""
        # In a real implementation:
        # message = Mail(
        #     from_email=self.from_email,
        #     to_emails=to_email,
        #     subject=subject,
        #     html_content=body
        # )
        # self.email_client.send(message)
        logger.info(f"Email would be sent to {to_email} with subject: {subject}")
    
    def _make_phone_call(self, to_number: str, script: str) -> None:
        """Make automated phone call with AI voice using script."""
        # In a real implementation, this would connect to a voice service
        # that can process the script using text-to-speech
        logger.info(f"Phone call would be made to {to_number} with script length {len(script)}")
    
    def send_question(self, participant_id: str, contact: str, 
                      method: str, question: str) -> None:
        """
        Send a single question to a participant using their preferred method.
        
        Args:
            participant_id: The participant identifier
            contact: Contact information (phone/email)
            method: Preferred communication method (sms, email, phone)
            question: The question to ask
        """
        if method == "sms" and self.sms_enabled:
            self._send_sms(contact, question)
        elif method == "email" and self.email_enabled:
            subject = "Quick question about your preferences"
            self._send_email(contact, subject, question)
        elif method == "phone" and self.voice_enabled:
            script = f"Hello, I have a question for you about your preferences. {question}"
            self._make_phone_call(contact, script)
        else:
            logger.warning(f"Could not send question to participant {participant_id}: method {method} unavailable")
    
    def send_plan_to_organizer(self, organizer_name: str, organizer_contact: str,
                              event_name: str, plan: Dict[str, Any]) -> None:
        """
        Send the generated plan to the organizer for approval.
        
        Args:
            organizer_name: Name of the event organizer
            organizer_contact: Contact information for the organizer
            event_name: Name of the event being planned
            plan: Dictionary containing the plan details
        """
        contact_type = self._detect_contact_type(organizer_contact)
        
        # Format the plan as a message
        plan_text = self._format_plan_for_message(plan)
        
        message = (
            f"Hi {organizer_name}, I've created a proposed plan for {event_name} "
            f"based on everyone's preferences:\n\n{plan_text}\n\n"
            f"Please reply with APPROVE to confirm this plan, or REVISE followed by "
            f"your feedback if you'd like changes."
        )
        
        # Send via appropriate channel
        if contact_type == "phone" and self.sms_enabled:
            # For SMS, we might need to split long messages
            self._send_sms(organizer_contact, message)
        elif contact_type == "email" and self.email_enabled:
            subject = f"Proposed Plan for {event_name}"
            self._send_email(organizer_contact, subject, message)
        else:
            logger.warning(f"Could not send plan to organizer: invalid contact info or method disabled")
    
    def send_plan_to_participant(self, participant_name: str, participant_contact: str,
                               preferred_method: str, event_name: str, 
                               organizer_name: str, plan: Dict[str, Any]) -> None:
        """
        Send the approved plan to a participant.
        
        Args:
            participant_name: Name of the participant
            participant_contact: Contact information for the participant
            preferred_method: Participant's preferred communication method
            event_name: Name of the event being planned
            organizer_name: Name of the event organizer
            plan: Dictionary containing the plan details
        """
        # Format the plan as a message
        plan_text = self._format_plan_for_message(plan)
        
        message = (
            f"Hi {participant_name}, {organizer_name} has approved the plan for {event_name}:\n\n"
            f"{plan_text}\n\n"
            f"Please reply with YES if this works for you, or NO followed by "
            f"any concerns if you have issues with this plan."
        )
        
        if preferred_method == "sms" and self.sms_enabled:
            self._send_sms(participant_contact, message)
        elif preferred_method == "email" and self.email_enabled:
            subject = f"Approved Plan for {event_name}"
            self._send_email(participant_contact, subject, message)
        elif preferred_method == "phone" and self.voice_enabled:
            script = f"Hello {participant_name}, I'm calling about the plan for {event_name}. {plan_text}"
            self._make_phone_call(participant_contact, script)
        else:
            # Fall back to SMS or email based on contact format
            contact_type = self._detect_contact_type(participant_contact)
            if contact_type == "phone" and self.sms_enabled:
                self._send_sms(participant_contact, message)
            elif contact_type == "email" and self.email_enabled:
                subject = f"Approved Plan for {event_name}"
                self._send_email(participant_contact, subject, message)
    
    def notify_organizer_of_rejection(self, organizer_name: str, organizer_contact: str,
                                     participant_name: str, event_name: str, feedback: str) -> None:
        """
        Notify the organizer when a participant rejects the plan.
        
        Args:
            organizer_name: Name of the event organizer
            organizer_contact: Contact information for the organizer
            participant_name: Name of the participant who rejected the plan
            event_name: Name of the event being planned
            feedback: Feedback from the participant
        """
        contact_type = self._detect_contact_type(organizer_contact)
        
        message = (
            f"Hi {organizer_name}, {participant_name} has concerns about the plan for {event_name}.\n\n"
            f"Their feedback: {feedback}\n\n"
            f"Would you like me to create a revised plan? Reply with YES to create a new plan, "
            f"or CONTINUE if you'd like to proceed with the current plan."
        )
        
        if contact_type == "phone" and self.sms_enabled:
            self._send_sms(organizer_contact, message)
        elif contact_type == "email" and self.email_enabled:
            subject = f"Feedback on Plan for {event_name}"
            self._send_email(organizer_contact, subject, message)
    
    def _format_plan_for_message(self, plan: Dict[str, Any]) -> str:
        """Format the plan dictionary into a readable message."""
        formatted = f"PLAN FOR: {plan.get('event_name', 'Event')}\n"
        formatted += f"DATE: {plan.get('date', 'TBD')}\n"
        formatted += f"TIME: {plan.get('time', 'TBD')}\n"
        formatted += f"LOCATION: {plan.get('location', 'TBD')}\n"
        formatted += f"ACTIVITIES: {', '.join(plan.get('activities', ['TBD']))}\n"
        
        if "notes" in plan and plan["notes"]:
            formatted += f"\nADDITIONAL NOTES:\n{plan['notes']}\n"
            
        return formatted
