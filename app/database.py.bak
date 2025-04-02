import sqlite3
import logging
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    """
    Handles all database operations for the AI Agent.
    Uses SQLite for simplicity, but could be replaced with any database.
    """
    
    def __init__(self, db_path: str = "planner.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables if they don't exist
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")
    
    def _create_tables(self) -> None:
        """Create necessary database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            organizer_name TEXT NOT NULL,
            organizer_contact TEXT NOT NULL,
            event_name TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # Participants table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            preferred_comm_method TEXT,
            preferences_complete BOOLEAN DEFAULT 0,
            awaiting_continuation BOOLEAN DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        ''')
        
        # Questions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            participant_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (participant_id) REFERENCES participants(id)
        )
        ''')
        
        # Responses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            participant_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            response_text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (participant_id) REFERENCES participants(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
        ''')
        
        # Plans table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            plan_data TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            feedback TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        ''')
        
        # Participant feedback on plans
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_feedback (
            id TEXT PRIMARY KEY,
            participant_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            accepted BOOLEAN NOT NULL,
            feedback TEXT,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (participant_id) REFERENCES participants(id),
            FOREIGN KEY (plan_id) REFERENCES plans(id)
        )
        ''')
        
        self.conn.commit()
    
    def create_session(self, organizer_name: str, organizer_contact: str, 
                      event_name: str, created_at: datetime) -> str:
        """
        Create a new planning session.
        
        Args:
            organizer_name: Name of the person organizing the activity
            organizer_contact: Contact info for the organizer
            event_name: Name of the event being planned
            created_at: Timestamp when the session was created
            
        Returns:
            session_id: Unique identifier for the session
        """
        session_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO sessions (id, organizer_name, organizer_contact, event_name, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (session_id, organizer_name, organizer_contact, event_name, created_at))
        
        self.conn.commit()
        return session_id
    
    def add_participant(self, session_id: str, name: str, contact: str) -> str:
        """
        Add a participant to a session.
        
        Args:
            session_id: The planning session identifier
            name: Participant's name
            contact: Participant's contact information
            
        Returns:
            participant_id: Unique identifier for the participant
        """
        participant_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO participants (id, session_id, name, contact)
        VALUES (?, ?, ?, ?)
        ''', (participant_id, session_id, name, contact))
        
        self.conn.commit()
        return participant_id
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            session: Dictionary with session information
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_participants(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all participants for a session.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            participants: List of dictionaries with participant information
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM participants WHERE session_id = ?', (session_id,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_participant(self, participant_id: str) -> Dict[str, Any]:
        """
        Get participant information.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            participant: Dictionary with participant information
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM participants WHERE id = ?', (participant_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_participant_contact(self, participant_id: str) -> str:
        """
        Get a participant's contact information.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            contact: Participant's contact information
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT contact FROM participants WHERE id = ?', (participant_id,))
        row = cursor.fetchone()
        
        if row:
            return row['contact']
        return None
    
    def set_preferred_comm_method(self, participant_id: str, method: str) -> None:
        """
        Set a participant's preferred communication method.
        
        Args:
            participant_id: The participant identifier
            method: Preferred method (sms, email, phone)
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE participants
        SET preferred_comm_method = ?
        WHERE id = ?
        ''', (method, participant_id))
        
        self.conn.commit()
    
    def get_preferred_comm_method(self, participant_id: str) -> str:
        """
        Get a participant's preferred communication method.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            method: Preferred communication method
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT preferred_comm_method FROM participants WHERE id = ?', (participant_id,))
        row = cursor.fetchone()
        
        if row and row['preferred_comm_method']:
            return row['preferred_comm_method']
        return None
    
    def store_question(self, participant_id: str, question_text: str) -> str:
        """
        Store a question sent to a participant.
        
        Args:
            participant_id: The participant identifier
            question_text: The text of the question
            
        Returns:
            question_id: Unique identifier for the question
        """
        question_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO questions (id, participant_id, question_text, created_at)
        VALUES (?, ?, ?, ?)
        ''', (question_id, participant_id, question_text, datetime.now()))
        
        self.conn.commit()
        return question_id
    
    def store_preference_response(self, participant_id: str, question_id: str, 
                                 response_text: str) -> str:
        """
        Store a participant's response to a question.
        
        Args:
            participant_id: The participant identifier
            question_id: The question identifier
            response_text: The participant's response
            
        Returns:
            response_id: Unique identifier for the response
        """
        response_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO responses (id, participant_id, question_id, response_text, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (response_id, participant_id, question_id, response_text, datetime.now()))
        
        self.conn.commit()
        return response_id
    
    def get_question_count(self, participant_id: str) -> int:
        """
        Get the number of questions that have been asked to a participant.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            count: Number of questions asked
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM questions WHERE participant_id = ?', (participant_id,))
        row = cursor.fetchone()
        
        return row['count'] if row else 0
    
    def set_awaiting_continuation(self, participant_id: str, awaiting: bool) -> None:
        """
        Set whether a participant is awaiting a continuation decision.
        
        Args:
            participant_id: The participant identifier
            awaiting: Whether they are awaiting a continuation decision
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE participants
        SET awaiting_continuation = ?
        WHERE id = ?
        ''', (1 if awaiting else 0, participant_id))
        
        self.conn.commit()
    
    def is_awaiting_continuation(self, participant_id: str) -> bool:
        """
        Check if a participant is awaiting a continuation decision.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            awaiting: Whether they are awaiting a continuation decision
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT awaiting_continuation FROM participants WHERE id = ?', (participant_id,))
        row = cursor.fetchone()
        
        return bool(row['awaiting_continuation']) if row else False
    
    def mark_preferences_complete(self, participant_id: str) -> None:
        """
        Mark a participant's preference collection as complete.
        
        Args:
            participant_id: The participant identifier
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE participants
        SET preferences_complete = 1
        WHERE id = ?
        ''', (participant_id,))
        
        self.conn.commit()
    
    def is_preference_collection_complete(self, participant_id: str) -> bool:
        """
        Check if a participant's preference collection is complete.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            complete: Whether preference collection is complete
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT preferences_complete FROM participants WHERE id = ?', (participant_id,))
        row = cursor.fetchone()
        
        return bool(row['preferences_complete']) if row else False
    
    def get_participant_responses(self, participant_id: str) -> List[Dict[str, Any]]:
        """
        Get all responses from a participant.
        
        Args:
            participant_id: The participant identifier
            
        Returns:
            responses: List of dictionaries with question and response information
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT q.id as question_id, q.question_text, r.id as response_id, r.response_text
        FROM questions q
        JOIN responses r ON q.id = r.question_id
        WHERE q.participant_id = ? AND r.participant_id = ?
        ORDER BY q.created_at
        ''', (participant_id, participant_id))
        rows = cursor.fetchall()
        
        return [{'question': row['question_text'], 'response': row['response_text']} for row in rows]
    
    def store_plan(self, session_id: str, plan: Dict[str, Any]) -> str:
        """
        Store a generated plan.
        
        Args:
            session_id: The planning session identifier
            plan: Dictionary containing the plan details
            
        Returns:
            plan_id: Unique identifier for the plan
        """
        plan_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO plans (id, session_id, plan_data, created_at)
        VALUES (?, ?, ?, ?)
        ''', (plan_id, session_id, json.dumps(plan), datetime.now()))
        
        self.conn.commit()
        return plan_id
    
    def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get a plan by ID.
        
        Args:
            plan_id: The plan identifier
            
        Returns:
            plan: Dictionary containing the plan details
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM plans WHERE id = ?', (plan_id,))
        row = cursor.fetchone()
        
        if row:
            plan_dict = dict(row)
            plan_dict['plan_data'] = json.loads(plan_dict['plan_data'])
            return plan_dict['plan_data']
        return None
    
    def get_latest_plan(self, session_id: str) -> Dict[str, Any]:
        """
        Get the most recent plan for a session.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            plan: Dictionary containing the plan details
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM plans 
        WHERE session_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
        ''', (session_id,))
        row = cursor.fetchone()
        
        if row:
            plan_dict = dict(row)
            plan_dict['plan_data'] = json.loads(plan_dict['plan_data'])
            return plan_dict['plan_data']
        return None
    
    def update_plan_status(self, plan_id: str, status: str, feedback: Optional[str] = None) -> None:
        """
        Update a plan's status.
        
        Args:
            plan_id: The plan identifier
            status: New status (pending, approved, rejected)
            feedback: Optional feedback about the status change
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE plans
        SET status = ?, feedback = ?
        WHERE id = ?
        ''', (status, feedback, plan_id))
        
        self.conn.commit()
    
    def get_latest_approved_plan_id(self, session_id: str) -> str:
        """
        Get the ID of the most recent approved plan for a session.
        
        Args:
            session_id: The planning session identifier
            
        Returns:
            plan_id: Identifier of the most recent approved plan
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id FROM plans 
        WHERE session_id = ? AND status = 'approved'
        ORDER BY created_at DESC 
        LIMIT 1
        ''', (session_id,))
        row = cursor.fetchone()
        
        return row['id'] if row else None
    
    def record_participant_feedback(self, participant_id: str, plan_id: str,
                                  accepted: bool, feedback: Optional[str] = None) -> str:
        """
        Record a participant's feedback on a plan.
        
        Args:
            participant_id: The participant identifier
            plan_id: The plan identifier
            accepted: Whether the participant accepted the plan
            feedback: Optional feedback from the participant
            
        Returns:
            feedback_id: Unique identifier for the feedback record
        """
        feedback_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO plan_feedback (id, participant_id, plan_id, accepted, feedback, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (feedback_id, participant_id, plan_id, 1 if accepted else 0, feedback, datetime.now()))
        
        self.conn.commit()
        return feedback_id
    
    def get_plan_feedback(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get all participant feedback for a plan.
        
        Args:
            plan_id: The plan identifier
            
        Returns:
            feedback: List of dictionaries with feedback information
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT pf.*, p.name as participant_name
        FROM plan_feedback pf
        JOIN participants p ON pf.participant_id = p.id
        WHERE pf.plan_id = ?
        ORDER BY pf.created_at
        ''', (plan_id,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
