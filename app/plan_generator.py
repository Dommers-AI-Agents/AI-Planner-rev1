import os
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

# In a real implementation, you would use the proper LLM client
# from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlanGenerator:
    """
    Generates optimal activity plans based on collected participant preferences.
    Uses LLM to analyze preferences and create plans that accommodate everyone.
    """
    
    def __init__(self, db, api_key: str = None):
        """Initialize the PlanGenerator with database connection."""
        self.db = db
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        # self.llm_client = Anthropic(api_key=self.api_key)
        
        logger.info("Plan Generator initialized")
    
    def create_plan(self, session_id: str) -> Dict[str, Any]:
        """
        Create an optimal plan based on all participants' preferences.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            plan: Dictionary containing the generated plan details
        """
        # Get session info
        session = self.db.get_session(session_id)
        participants = self.db.get_participants(session_id)
        
        # Collect all preferences
        all_preferences = {}
        for participant in participants:
            responses = self.db.get_participant_responses(participant['id'])
            all_preferences[participant['name']] = {
                'responses': responses,
                'preferred_comm_method': self.db.get_preferred_comm_method(participant['id'])
            }
        
        # In a real implementation, use LLM to generate the plan:
        # prompt = self._construct_planning_prompt(session, all_preferences)
        # response = self.llm_client.completions.create(
        #     model="claude-3-opus-20240229",
        #     prompt=prompt,
        #     max_tokens_to_sample=2000,
        #     temperature=0.2,
        #     response_format={"type": "json"}
        # )
        # plan_json = json.loads(response.completion)
        
        # For this example, create a simple mock plan
        plan = self._create_mock_plan(session, all_preferences)
        
        logger.info(f"Created plan for session {session_id}")
        return plan
    
    def _construct_planning_prompt(self, session: Dict[str, Any], 
                                  all_preferences: Dict[str, Dict[str, Any]]) -> str:
        """
        Construct a detailed prompt for the LLM to generate an optimal plan.
        
        Args:
            session: Session information
            all_preferences: Dictionary of all participants' preferences
            
        Returns:
            prompt: The full prompt for the LLM
        """
        # Format all preferences as text
        preferences_text = ""
        for name, data in all_preferences.items():
            preferences_text += f"\n\nPreferences for {name}:\n"
            for resp in data['responses']:
                preferences_text += f"Q: {resp['question']}\nA: {resp['response']}\n"
        
        prompt = f"""{HUMAN_PROMPT}
You are an expert event planner. I need you to create an optimal plan for an event based on everyone's preferences.

EVENT DETAILS:
- Event Name: {session['event_name']}
- Organizer: {session['organizer_name']}
- Number of Participants: {len(all_preferences)}

PARTICIPANT PREFERENCES:{preferences_text}

Based on these preferences, create an optimal plan that accommodates everyone's needs as much as possible. Focus especially on:
1. Finding a date and time that works for everyone
2. Choosing activities that align with participants' interests
3. Selecting appropriate locations
4. Accommodating any special needs (children, accessibility, dietary restrictions)
5. Optimizing for everyone's stated priorities

Return the plan as a JSON object with the following structure:
{{
  "event_name": "string",
  "date": "string (YYYY-MM-DD)",
  "time": "string (e.g. '7:00 PM - 9:00 PM')",
  "location": "string",
  "activities": ["string", "string", ...],
  "accommodations": {{
    "key": "value"
  }},
  "notes": "string with any important details",
  "reasoning": "string explaining why this plan works well for everyone"
}}

Only return the JSON object, with no additional text.{AI_PROMPT}"""
        
        return prompt
    
    def _create_mock_plan(self, session: Dict[str, Any], 
                         all_preferences: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a mock plan for demonstration purposes.
        
        Args:
            session: Session information
            all_preferences: Dictionary of all participants' preferences
            
        Returns:
            plan: Dictionary containing the generated plan details
        """
        # For demo purposes, create a simple plan
        now = datetime.now()
        next_saturday = now.replace(day=now.day + ((12 - now.weekday()) % 7))
        
        plan = {
            "event_name": session["event_name"],
            "date": next_saturday.strftime("%Y-%m-%d"),
            "time": "2:00 PM - 5:00 PM",
            "location": "Central Park",
            "activities": ["Picnic", "Board Games", "Nature Walk"],
            "accommodations": {
                "dietary": "Vegetarian options available",
                "accessibility": "Accessible paths available",
                "children": "Playground nearby for kids"
            },
            "notes": "In case of rain, we'll meet at Coffee House on Main St instead. Everyone should bring a water bottle and comfortable shoes.",
            "reasoning": "This plan accommodates everyone's schedule preferences while providing a mix of activities that align with participants' interests. The location is centrally located and offers options for both active and passive participation."
        }
        
        return plan
    
    def revise_plan(self, session_id: str, plan_id: str, 
                   feedback: str, participant_id: str = None) -> Dict[str, Any]:
        """
        Revise an existing plan based on feedback.
        
        Args:
            session_id: The planning session identifier
            plan_id: The identifier of the plan to revise
            feedback: Feedback to incorporate
            participant_id: Optional identifier of the participant providing feedback
            
        Returns:
            revised_plan: Dictionary containing the revised plan
        """
        # Get the existing plan
        existing_plan = self.db.get_plan(plan_id)
        
        # Get all preferences again
        participants = self.db.get_participants(session_id)
        all_preferences = {}
        for participant in participants:
            responses = self.db.get_participant_responses(participant['id'])
            all_preferences[participant['name']] = {
                'responses': responses,
                'preferred_comm_method': self.db.get_preferred_comm_method(participant['id'])
            }
        
        # Get session info
        session = self.db.get_session(session_id)
        
        # Get participant name if participant_id provided
        participant_name = None
        if participant_id:
            participant = self.db.get_participant(participant_id)
            participant_name = participant['name']
        
        # In a real implementation, use LLM to revise the plan:
        # prompt = self._construct_revision_prompt(session, existing_plan, feedback, 
        #                                         participant_name, all_preferences)
        # response = self.llm_client.completions.create(
        #     model="claude-3-opus-20240229",
        #     prompt=prompt,
        #     max_tokens_to_sample=2000,
        #     temperature=0.2,
        #     response_format={"type": "json"}
        # )
        # revised_plan_json = json.loads(response.completion)
        
        # For this example, create a simple revised plan
        revised_plan = self._create_mock_revised_plan(existing_plan, feedback, participant_name)
        
        logger.info(f"Revised plan for session {session_id} based on feedback")
        return revised_plan
    
    def _create_mock_revised_plan(self, existing_plan: Dict[str, Any], 
                                feedback: str, participant_name: str = None) -> Dict[str, Any]:
        """
        Create a mock revised plan for demonstration purposes.
        
        Args:
            existing_plan: The existing plan to revise
            feedback: Feedback to incorporate
            participant_name: Optional name of the participant providing feedback
            
        Returns:
            revised_plan: Dictionary containing the revised plan
        """
        # Copy the existing plan
        revised_plan = existing_plan.copy()
        
        # Make some simple modifications based on feedback keywords
        if "time" in feedback.lower():
            # Adjust the time
            revised_plan["time"] = "3:00 PM - 6:00 PM"
            revised_plan["notes"] = (revised_plan.get("notes", "") + 
                                    "\nTime adjusted based on participant feedback.")
        
        if "location" in feedback.lower():
            # Change the location
            revised_plan["location"] = "Riverside Park"
            revised_plan["notes"] = (revised_plan.get("notes", "") + 
                                    "\nLocation changed based on participant feedback.")
        
        if "activity" in feedback.lower() or "activities" in feedback.lower():
            # Modify activities
            revised_plan["activities"] = ["Picnic", "Frisbee", "Card Games"]
            revised_plan["notes"] = (revised_plan.get("notes", "") + 
                                    "\nActivities adjusted based on participant preferences.")
        
        # Add revision reason
        revised_plan["revision_reason"] = f"Plan revised based on feedback"
        if participant_name:
            revised_plan["revision_reason"] += f" from {participant_name}"
        
        return revised_plan
