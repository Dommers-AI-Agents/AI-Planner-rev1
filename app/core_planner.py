import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from communication_handler import CommunicationHandler
from preference_collector import PreferenceCollector
from plan_generator import PlanGenerator
from database import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CorePlanner:
    """
    Main orchestration class for the Group Activity Planning AI Agent.
    Manages the overall planning process from participant outreach to plan generation.
    """
    
    def __init__(self, db_path: str = "planner.db"):
        """Initialize the CorePlanner with necessary components."""
        self.db = Database(db_path)
        self.comm_handler = CommunicationHandler()
        self.preference_collector = PreferenceCollector(self.db, self.comm_handler)
        self.plan_generator = PlanGenerator(self.db)
        logger.info("Core Planner initialized")
        
    def create_planning_session(self, organizer_name: str, organizer_contact: str, 
                               event_name: str, participants: List[Dict[str, str]]) -> str:
        """
        Create a new planning session.
        
        Args:
            organizer_name: Name of the person organizing the activity
            organizer_contact: Contact info for the organizer
            event_name: Name of the event being planned
            participants: List of participant info dictionaries with name and contact
            
        Returns:
            session_id: Unique identifier for the planning session
        """
        session_id = self.db.create_session(
            organizer_name=organizer_name,
            organizer_contact=organizer_contact,
            event_name=event_name,
            created_at=datetime.now()
        )
        
        # Add participants to the session
        for participant in participants:
            self.db.add_participant(
                session_id=session_id,
                name=participant['name'],
                contact=participant['contact']
            )
            
        logger.info(f"Created planning session {session_id} for {event_name} by {organizer_name}")
        return session_id
    
    def start_outreach(self, session_id: str) -> None:
        """
        Begin the outreach process to all participants.
        
        Args:
            session_id: The planning session identifier
        """
        # Get session details
        session = self.db.get_session(session_id)
        participants = self.db.get_participants(session_id)
        
        logger.info(f"Starting outreach for session {session_id} with {len(participants)} participants")
        
        # Begin outreach to each participant
        for participant in participants:
            self.comm_handler.initiate_contact(
                session_id=session_id,
                participant_id=participant['id'],
                participant_name=participant['name'],
                participant_contact=participant['contact'],
                organizer_name=session['organizer_name'],
                event_name=session['event_name']
            )
    
    def check_preferences_status(self, session_id: str) -> Dict[str, Any]:
        """
        Check the status of preference collection for all participants.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            status: Dictionary with completion status and participant details
        """
        participants = self.db.get_participants(session_id)
        completed = [p for p in participants if self.db.is_preference_collection_complete(p['id'])]
        
        return {
            'total_participants': len(participants),
            'completed': len(completed),
            'pending': len(participants) - len(completed),
            'complete_percentage': (len(completed) / len(participants)) * 100 if participants else 0,
            'participant_status': [
                {
                    'name': p['name'],
                    'status': 'complete' if p in completed else 'pending',
                    'preferred_comm_method': self.db.get_preferred_comm_method(p['id'])
                }
                for p in participants
            ]
        }
    
    def generate_plan(self, session_id: str) -> Dict[str, Any]:
        """
        Generate a plan based on collected preferences.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            plan: Dictionary containing the generated plan details
        """
        # Check if all preferences have been collected
        status = self.check_preferences_status(session_id)
        if status['pending'] > 0:
            logger.warning(f"Not all preferences collected for session {session_id}. Generating with available data.")
        
        # Generate the plan
        plan = self.plan_generator.create_plan(session_id)
        
        # Store the plan in the database
        plan_id = self.db.store_plan(session_id, plan)
        
        logger.info(f"Generated plan {plan_id} for session {session_id}")
        return plan
    
    def submit_plan_to_organizer(self, session_id: str) -> None:
        """
        Send the generated plan to the organizer for approval.
        
        Args:
            session_id: The planning session identifier
        """
        session = self.db.get_session(session_id)
        plan = self.db.get_latest_plan(session_id)
        
        self.comm_handler.send_plan_to_organizer(
            organizer_name=session['organizer_name'],
            organizer_contact=session['organizer_contact'],
            event_name=session['event_name'],
            plan=plan
        )
        
        logger.info(f"Submitted plan to organizer for session {session_id}")
    
    def record_organizer_decision(self, session_id: str, plan_id: str, approved: bool, feedback: Optional[str] = None) -> None:
        """
        Record the organizer's decision on the proposed plan.
        
        Args:
            session_id: The planning session identifier
            plan_id: The plan identifier
            approved: Whether the organizer approved the plan
            feedback: Optional feedback from the organizer
        """
        self.db.update_plan_status(plan_id, 'approved' if approved else 'rejected', feedback)
        
        if approved:
            self.distribute_plan_to_participants(session_id, plan_id)
        else:
            # Regenerate plan if needed
            logger.info(f"Organizer rejected plan {plan_id} for session {session_id}. Feedback: {feedback}")
            
    def distribute_plan_to_participants(self, session_id: str, plan_id: str) -> None:
        """
        Send the approved plan to all participants.
        
        Args:
            session_id: The planning session identifier
            plan_id: The identifier of the approved plan
        """
        participants = self.db.get_participants(session_id)
        plan = self.db.get_plan(plan_id)
        session = self.db.get_session(session_id)
        
        for participant in participants:
            self.comm_handler.send_plan_to_participant(
                participant_name=participant['name'],
                participant_contact=participant['contact'],
                preferred_method=self.db.get_preferred_comm_method(participant['id']),
                event_name=session['event_name'],
                organizer_name=session['organizer_name'],
                plan=plan
            )
            
        logger.info(f"Distributed plan {plan_id} to {len(participants)} participants for session {session_id}")
    
    def collect_participant_feedback(self, session_id: str, participant_id: str, 
                                     accepted: bool, feedback: Optional[str] = None) -> None:
        """
        Collect feedback from a participant on the proposed plan.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            accepted: Whether the participant accepted the plan
            feedback: Optional feedback from the participant
        """
        plan_id = self.db.get_latest_approved_plan_id(session_id)
        
        self.db.record_participant_feedback(
            participant_id=participant_id,
            plan_id=plan_id,
            accepted=accepted,
            feedback=feedback
        )
        
        if not accepted and feedback:
            # Notify organizer about the rejection and feedback
            session = self.db.get_session(session_id)
            participant = self.db.get_participant(participant_id)
            
            self.comm_handler.notify_organizer_of_rejection(
                organizer_name=session['organizer_name'],
                organizer_contact=session['organizer_contact'],
                participant_name=participant['name'],
                event_name=session['event_name'],
                feedback=feedback
            )
            
            logger.info(f"Participant {participant_id} rejected plan for session {session_id}. Feedback: {feedback}")
