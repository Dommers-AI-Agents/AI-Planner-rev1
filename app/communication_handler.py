import os
import logging
from typing import Dict, Any, Optional, List
import json
from urllib.parse import quote

# Placeholder for actual communication APIs
# In a real implementation, you would import proper libraries:
# import twilio.rest
# from sendgrid import SendGridAPIClient
# from anthropic import Anthropic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommunicationHandler:
    """
    Handles external communications with participants and organizers
    via SMS, email, and website links.
    """
    
    def __init__(self, 
                 sms_enabled: bool = True, 
                 email_enabled: bool = True, 
                 base_url: str = "https://planner.yourdomain.com",
                 api_key: Optional[str] = None):
        """Initialize the CommunicationHandler with configuration."""
        self.sms_enabled = sms_enabled
        self.email_enabled = email_enabled
        self.base_url = base_url
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        
        # Setup communication clients
        # self.twilio_client = twilio.rest.Client(account_sid, auth_token) 
        # self.email_client = SendGridAPIClient(sendgrid_api_key)
        # self.llm_client = Anthropic(api_key=self.api_key)
        
        logger.info("Communication Handler initialized")
    
    def _generate_participant_link(self, session_id: str, participant_id: str) -> str:
        """Generate a unique URL for the participant to access the web interface."""
        return f"{self.base_url}/participant?session_id={session_id}&participant_id={participant_id}"
        
    def initiate_contact(self, session_id: str, participant_id: str, 
                         participant_name: str, participant_contact: str,
                         organizer_name: str, event_name: str) -> None:
        """
        Initiates first contact with a participant to introduce the AI agent
        and provides a link to the web interface for preference collection.
        
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
        
        # Generate unique participant link
        participant_link = self._generate_participant_link(session_id, participant_id)
        
        # Initial message template with web link
        message = (
            f"Hi {participant_name}, {organizer_name} is planning {event_name} "
            f"and has asked me (an AI assistant) to help coordinate. "
            f"Please visit this link to share your preferences and help plan the event: "
            f"{participant_link}"
        )
        
        # Send via appropriate channel
        if contact_type == "phone" and self.sms_enabled:
            self._send_sms(participant_contact, message)
            logger.info(f"Sent initial SMS with web link to {participant_name} for session {session_id}")
        elif contact_type == "email" and self.email_enabled:
            subject = f"Help Plan: {event_name} with {organizer_name}"
            email_body = f"""
            <html>
            <body>
            <p>Hi {participant_name},</p>
            <p>{organizer_name} is planning <strong>{event_name}</strong> and has asked me (an AI assistant) to help coordinate.</p>
            <p>Please click the button below to share your preferences and help plan the event:</p>
            <p style="text-align: center;">
                <a href="{participant_link}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">
                    Share Your Preferences
                </a>
            </p>
            <p>Thank you for your help in making this event a success!</p>
            </body>
            </html>
            """
            self._send_email(participant_contact, subject, email_body)
            logger.info(f"Sent initial email with web link to {participant_name} for session {session_id}")
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
    
    def send_reminder(self, session_id: str, participant_id: str, 
                    participant_name: str, contact: str, 
                    method: str, event_name: str) -> None:
        """
        Send a reminder to a participant to complete their preferences on the web interface.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            participant_name: Name of the participant
            contact: Contact information (phone/email)
            method: Preferred communication method (sms, email)
            event_name: Name of the event being planned
        """
        # Generate the participant link
        participant_link = self._generate_participant_link(session_id, participant_id)
        
        # Create reminder message
        message = (
            f"Hi {participant_name}, this is a friendly reminder to share your preferences "
            f"for the {event_name} event. Your input will help us plan the best possible experience. "
            f"Please visit: {participant_link}"
        )
        
        # Send via appropriate channel
        if method == "sms" and self.sms_enabled:
            self._send_sms(contact, message)
        elif method == "email" and self.email_enabled:
            subject = f"Reminder: Share your preferences for {event_name}"
            email_body = f"""
            <html>
            <body>
            <p>Hi {participant_name},</p>
            <p>This is a friendly reminder to share your preferences for the <strong>{event_name}</strong> event.</p>
            <p>Your input will help us plan the best possible experience for everyone.</p>
            <p style="text-align: center;">
                <a href="{participant_link}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">
                    Complete Your Preferences
                </a>
            </p>
            <p>Thank you for your help!</p>
            </body>
            </html>
            """
            self._send_email(contact, subject, email_body)
        else:
            logger.warning(f"Could not send reminder to participant {participant_id}: method {method} unavailable")
    
    def _generate_organizer_link(self, session_id: str) -> str:
        """Generate a unique URL for the organizer to access the web interface."""
        return f"{self.base_url}/organizer?session_id={session_id}"
        
    def send_plan_to_organizer(self, session_id: str, organizer_name: str, organizer_contact: str,
                              event_name: str, plan: Dict[str, Any]) -> None:
        """
        Send the generated plan to the organizer for approval via the web interface.
        
        Args:
            session_id: The planning session identifier
            organizer_name: Name of the event organizer
            organizer_contact: Contact information for the organizer
            event_name: Name of the event being planned
            plan: Dictionary containing the plan details
        """
        contact_type = self._detect_contact_type(organizer_contact)
        
        # Generate organizer link
        organizer_link = self._generate_organizer_link(session_id)
        
        # Format the plan summary for the message
        plan_summary = (
            f"Date: {plan.get('date', 'TBD')}, "
            f"Time: {plan.get('time', 'TBD')}, "
            f"Location: {plan.get('location', 'TBD')}"
        )
        
        message = (
            f"Hi {organizer_name}, I've created a proposed plan for {event_name} "
            f"based on everyone's preferences. Here's a quick summary: {plan_summary}\n\n"
            f"Please visit this link to review the full plan and provide your decision: "
            f"{organizer_link}"
        )
        
        # Send via appropriate channel
        if contact_type == "phone" and self.sms_enabled:
            self._send_sms(organizer_contact, message)
        elif contact_type == "email" and self.email_enabled:
            subject = f"Proposed Plan for {event_name}"
            email_body = f"""
            <html>
            <body>
            <p>Hi {organizer_name},</p>
            <p>I've created a proposed plan for <strong>{event_name}</strong> based on everyone's preferences.</p>
            <p><strong>Summary:</strong> {plan_summary}</p>
            <p>Please click the button below to review the full plan and provide your decision:</p>
            <p style="text-align: center;">
                <a href="{organizer_link}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">
                    Review Plan
                </a>
            </p>
            <p>Thank you!</p>
            </body>
            </html>
            """
            self._send_email(organizer_contact, subject, email_body)
        else:
            logger.warning(f"Could not send plan to organizer: invalid contact info or method disabled")
    
    def send_plan_to_participant(self, session_id: str, participant_id: str,
                               participant_name: str, participant_contact: str,
                               preferred_method: str, event_name: str, 
                               organizer_name: str, plan: Dict[str, Any]) -> None:
        """
        Send the approved plan to a participant with a link to view details and provide feedback.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            participant_name: Name of the participant
            participant_contact: Contact information for the participant
            preferred_method: Participant's preferred communication method
            event_name: Name of the event being planned
            organizer_name: Name of the event organizer
            plan: Dictionary containing the plan details
        """
        # Generate participant link to specific plan review page
        participant_link = f"{self._generate_participant_link(session_id, participant_id)}&plan=approved"
        
        # Format the plan summary for the message
        plan_summary = (
            f"Date: {plan.get('date', 'TBD')}, "
            f"Time: {plan.get('time', 'TBD')}, "
            f"Location: {plan.get('location', 'TBD')}"
        )
        
        message = (
            f"Hi {participant_name}, {organizer_name} has approved the plan for {event_name}. "
            f"Quick summary: {plan_summary}\n\n"
            f"Please visit this link to view the full plan and confirm if it works for you: "
            f"{participant_link}"
        )
        
        if preferred_method == "sms" and self.sms_enabled:
            self._send_sms(participant_contact, message)
        elif preferred_method == "email" and self.email_enabled:
            subject = f"Approved Plan for {event_name}"
            email_body = f"""
            <html>
            <body>
            <p>Hi {participant_name},</p>
            <p><strong>{organizer_name}</strong> has approved the plan for <strong>{event_name}</strong>!</p>
            <p><strong>Summary:</strong> {plan_summary}</p>
            <p>Please click the button below to view the full plan and confirm if it works for you:</p>
            <p style="text-align: center;">
                <a href="{participant_link}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">
                    View & Confirm Plan
                </a>
            </p>
            <p>Thank you for your participation!</p>
            </body>
            </html>
            """
            self._send_email(participant_contact, subject, email_body)
        else:
            # Fall back to SMS or email based on contact format
            contact_type = self._detect_contact_type(participant_contact)
            if contact_type == "phone" and self.sms_enabled:
                self._send_sms(participant_contact, message)
            elif contact_type == "email" and self.email_enabled:
                subject = f"Approved Plan for {event_name}"
                self._send_email(participant_contact, subject, email_body)
    
    def notify_organizer_of_rejection(self, session_id: str, organizer_name: str, organizer_contact: str,
                                     participant_name: str, event_name: str, feedback: str) -> None:
        """
        Notify the organizer when a participant rejects the plan with a link to respond.
        
        Args:
            session_id: The planning session identifier
            organizer_name: Name of the event organizer
            organizer_contact: Contact information for the organizer
            participant_name: Name of the participant who rejected the plan
            event_name: Name of the event being planned
            feedback: Feedback from the participant
        """
        contact_type = self._detect_contact_type(organizer_contact)
        
        # Generate organizer link with feedback notification
        organizer_link = f"{self._generate_organizer_link(session_id)}&feedback=true"
        
        message = (
            f"Hi {organizer_name}, {participant_name} has concerns about the plan for {event_name}.\n\n"
            f"Their feedback: {feedback}\n\n"
            f"Please visit this link to decide whether to revise the plan or proceed: "
            f"{organizer_link}"
        )
        
        if contact_type == "phone" and self.sms_enabled:
            self._send_sms(organizer_contact, message)
        elif contact_type == "email" and self.email_enabled:
            subject = f"Feedback on Plan for {event_name}"
            email_body = f"""
            <html>
            <body>
            <p>Hi {organizer_name},</p>
            <p><strong>{participant_name}</strong> has concerns about the plan for <strong>{event_name}</strong>.</p>
            <p><strong>Their feedback:</strong> {feedback}</p>
            <p>Please click the button below to decide whether to revise the plan or proceed:</p>
            <p style="text-align: center;">
                <a href="{organizer_link}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">
                    Respond to Feedback
                </a>
            </p>
            </body>
            </html>
            """
            self._send_email(organizer_contact, subject, email_body)
    
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
