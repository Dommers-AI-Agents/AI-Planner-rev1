import os
import logging
from typing import Dict, Any, List, Optional
import json

# In a real implementation, you would use the proper LLM client
# from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreferenceCollector:
    """
    Collects and manages participant preferences through conversation.
    Uses LLM to generate dynamic questions based on previous responses.
    """
    
    def __init__(self, db, comm_handler, api_key: Optional[str] = None):
        """Initialize the PreferenceCollector with database and communication handler."""
        self.db = db
        self.comm_handler = comm_handler
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        # self.llm_client = Anthropic(api_key=self.api_key)
        
        # Base questions that can be asked to participants
        self.base_questions = [
            "What days of the week generally work best for you?",
            "What time of day do you prefer for activities?",
            "What types of activities do you enjoy most?",
            "Do you have any location preferences or restrictions?",
            "Are there any dietary restrictions or preferences I should know about?",
            "Do you have any mobility or accessibility needs?",
            "Are you bringing children, and if so, what are their ages?",
            "What's your comfort level with different types of transportation?",
            "Are there any budget considerations I should be aware of?",
            "What's most important to you for this event (e.g., socializing, specific activity, etc.)?"
        ]
        
        logger.info("Preference Collector initialized")
    
    def process_preferred_comm_method(self, session_id: str, participant_id: str, 
                                     response: str) -> None:
        """
        Process a participant's response about their preferred communication method.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            response: The participant's response text
        """
        # Normalize response
        response = response.strip().lower()
        
        method = None
        if response in ["1", "text", "sms", "txt"]:
            method = "sms"
        elif response in ["2", "email", "e-mail", "mail"]:
            method = "email"
        elif response in ["3", "phone", "call", "voice"]:
            method = "phone"
        else:
            # If response is unclear, default to the method they used to respond
            contact_info = self.db.get_participant_contact(participant_id)
            method = "email" if "@" in contact_info else "sms"
            logger.info(f"Unclear communication preference from participant {participant_id}, defaulting to {method}")
        
        # Store the preferred method
        self.db.set_preferred_comm_method(participant_id, method)
        
        # Send first question
        self._send_next_question(session_id, participant_id)
    
    def process_question_response(self, session_id: str, participant_id: str, 
                                 question_id: str, response: str) -> None:
        """
        Process a participant's response to a preference question.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            question_id: The identifier of the question being answered
            response: The participant's response text
        """
        # Store the response
        self.db.store_preference_response(participant_id, question_id, response)
        
        # Get current question count for this participant
        question_count = self.db.get_question_count(participant_id)
        
        if question_count >= 5:
            # Ask if they want to continue or stop
            participant = self.db.get_participant(participant_id)
            message = (
                "Thank you for your responses so far! Would you be willing to answer "
                "a few more questions to help plan the perfect event? Reply with YES "
                "to continue or NO to finish."
            )
            self.comm_handler.send_question(
                participant_id=participant_id,
                contact=participant['contact'],
                method=self.db.get_preferred_comm_method(participant_id),
                question=message
            )
            # Mark as awaiting continuation decision
            self.db.set_awaiting_continuation(participant_id, True)
        else:
            # Send next question
            self._send_next_question(session_id, participant_id)
    
    def process_continuation_response(self, session_id: str, participant_id: str, 
                                     response: str) -> None:
        """
        Process a participant's response about continuing with more questions.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
            response: The participant's response text
        """
        # Normalize response
        response = response.strip().lower()
        
        # Reset the awaiting continuation flag
        self.db.set_awaiting_continuation(participant_id, False)
        
        if response in ["yes", "y", "sure", "ok", "okay", "continue"]:
            # They want to continue, send next question
            self._send_next_question(session_id, participant_id)
        else:
            # They want to stop, mark preferences as complete
            self.db.mark_preferences_complete(participant_id)
            
            # Send thank you message
            participant = self.db.get_participant(participant_id)
            message = (
                "Thank you for sharing your preferences! I'll use this information "
                "to help create a plan that works for everyone. You'll receive the "
                "proposed plan once it's ready."
            )
            self.comm_handler.send_question(
                participant_id=participant_id,
                contact=participant['contact'],
                method=self.db.get_preferred_comm_method(participant_id),
                question=message
            )
    
    def _send_next_question(self, session_id: str, participant_id: str) -> None:
        """
        Generate and send the next appropriate question to a participant.
        
        Args:
            session_id: The planning session identifier
            participant_id: The participant identifier
        """
        # Get participant info
        participant = self.db.get_participant(participant_id)
        
        # Get previous responses to inform next question
        previous_responses = self.db.get_participant_responses(participant_id)
        
        # Determine next question
        next_question = self._generate_next_question(previous_responses)
        
        # Store the question
        question_id = self.db.store_question(participant_id, next_question)
        
        # Send the question
        self.comm_handler.send_question(
            participant_id=participant_id,
            contact=participant['contact'],
            method=self.db.get_preferred_comm_method(participant_id),
            question=next_question
        )
        
        logger.info(f"Sent question to participant {participant_id}: {next_question[:50]}...")
    
    def _generate_next_question(self, previous_responses: List[Dict[str, Any]]) -> str:
        """
        Generate the next question based on previous responses using LLM.
        
        Args:
            previous_responses: List of previous questions and responses
            
        Returns:
            next_question: The text of the next question to ask
        """
        # If no previous responses, use the first base question
        if not previous_responses:
            return self.base_questions[0]
        
        # If we have fewer responses than base questions, use the next base question
        question_count = len(previous_responses)
        if question_count < len(self.base_questions):
            return self.base_questions[question_count]
        
        # For dynamic question generation with LLM (in a real implementation):
        # Convert previous responses to context
        context = "\n".join([
            f"Q: {resp['question']}\nA: {resp['response']}"
            for resp in previous_responses
        ])
        
        # In a real implementation, use the LLM to generate a dynamic question:
        # response = self.llm_client.completions.create(
        #     model="claude-3-sonnet-20240229",
        #     prompt=f"{HUMAN_PROMPT} I'm planning an event and have gathered these preferences from a participant:\n\n{context}\n\nBased on their previous answers, what's an insightful follow-up question I should ask to better understand their needs and preferences for this event? The question should be specific, relevant to their previous answers, and help me plan better. Please provide just the question text without additional explanation.{AI_PROMPT}",
        #     max_tokens_to_sample=150,
        #     temperature=0.7
        # )
        # return response.completion.strip()
        
        # For this example, return a generic follow-up question
        return "Based on what you've shared so far, is there anything specific that would make this event perfect for you?"
