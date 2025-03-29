import os
import logging
import argparse
import json
from typing import List, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core_planner import CorePlanner
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("planner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Group Activity Planning AI Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core planner
planner = CorePlanner(db_path="planner.db")

# Define request/response models
class Participant(BaseModel):
    name: str
    contact: str

class CreateSessionRequest(BaseModel):
    organizer_name: str
    organizer_contact: str
    event_name: str
    participants: List[Participant]

class CreateSessionResponse(BaseModel):
    session_id: str
    message: str

class MessageResponse(BaseModel):
    message: str

class PreferenceRequest(BaseModel):
    session_id: str
    participant_id: str
    question_id: str
    response: str

class CommunicationPrefRequest(BaseModel):
    session_id: str
    participant_id: str
    preference: str

class OrganizerDecisionRequest(BaseModel):
    session_id: str
    plan_id: str
    approved: bool
    feedback: str = None

class ParticipantFeedbackRequest(BaseModel):
    session_id: str
    participant_id: str
    accepted: bool
    feedback: str = None

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest, background_tasks: BackgroundTasks):
    """Create a new planning session and initiate outreach to participants."""
    try:
        # Create participants list in the format expected by core_planner
        participants = [{"name": p.name, "contact": p.contact} for p in request.participants]
        
        # Create the planning session
        session_id = planner.create_planning_session(
            organizer_name=request.organizer_name,
            organizer_contact=request.organizer_contact,
            event_name=request.event_name,
            participants=participants
        )
        
        # Start outreach in the background
        background_tasks.add_task(planner.start_outreach, session_id)
        
        return {"session_id": session_id, "message": f"Planning session created for {request.event_name}"}
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get the current status of a planning session."""
    try:
        # Check if session exists
        session = planner.db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get preference collection status
        status = planner.check_preferences_status(session_id)
        
        # Get plan status if available
        latest_plan = planner.db.get_latest_plan(session_id)
        plan_status = None
        if latest_plan:
            plan_id = planner.db.get_latest_approved_plan_id(session_id)
            plan_status = {
                "has_plan": True,
                "plan_approved": plan_id is not None,
                "plan_details": latest_plan
            }
        else:
            plan_status = {"has_plan": False}
        
        return {
            "session_id": session_id,
            "event_name": session["event_name"],
            "organizer": session["organizer_name"],
            "created_at": session["created_at"],
            "preferences_status": status,
            "plan_status": plan_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preferences/comm-method", response_model=MessageResponse)
async def set_communication_preference(request: CommunicationPrefRequest):
    """Set a participant's preferred communication method."""
    try:
        planner.preference_collector.process_preferred_comm_method(
            session_id=request.session_id,
            participant_id=request.participant_id,
            response=request.preference
        )
        return {"message": "Communication preference set successfully"}
    except Exception as e:
        logger.error(f"Error setting communication preference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preferences/response", response_model=MessageResponse)
async def process_preference_response(request: PreferenceRequest):
    """Process a participant's response to a preference question."""
    try:
        # Check if participant is awaiting continuation decision
        if planner.db.is_awaiting_continuation(request.participant_id):
            planner.preference_collector.process_continuation_response(
                session_id=request.session_id,
                participant_id=request.participant_id,
                response=request.response
            )
        else:
            planner.preference_collector.process_question_response(
                session_id=request.session_id,
                participant_id=request.participant_id,
                question_id=request.question_id,
                response=request.response
            )
        return {"message": "Response processed successfully"}
    except Exception as e:
        logger.error(f"Error processing preference response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plans/generate/{session_id}", response_model=MessageResponse)
async def generate_plan(session_id: str, background_tasks: BackgroundTasks):
    """Generate a plan for a session and submit it to the organizer."""
    try:
        # Check if session exists
        session = planner.db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate the plan in the background
        background_tasks.add_task(planner.generate_plan, session_id)
        # Submit to organizer in the background
        background_tasks.add_task(planner.submit_plan_to_organizer, session_id)
        
        return {"message": "Plan generation started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plans/organizer-decision", response_model=MessageResponse)
async def record_organizer_decision(request: OrganizerDecisionRequest, background_tasks: BackgroundTasks):
    """Record the organizer's decision on a proposed plan."""
    try:
        planner.record_organizer_decision(
            session_id=request.session_id,
            plan_id=request.plan_id,
            approved=request.approved,
            feedback=request.feedback
        )
        
        return {"message": "Organizer decision recorded successfully"}
    except Exception as e:
        logger.error(f"Error recording organizer decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plans/participant-feedback", response_model=MessageResponse)
async def record_participant_feedback(request: ParticipantFeedbackRequest):
    """Record a participant's feedback on the proposed plan."""
    try:
        planner.collect_participant_feedback(
            session_id=request.session_id,
            participant_id=request.participant_id,
            accepted=request.accepted,
            feedback=request.feedback
        )
        
        return {"message": "Participant feedback recorded successfully"}
    except Exception as e:
        logger.error(f"Error recording participant feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/sms")
async def sms_webhook(From: str = None, Body: str = None):
    """Webhook for receiving SMS responses from participants."""
    try:
        if not From or not Body:
            raise HTTPException(status_code=400, detail="Missing From or Body parameters")
        
        # In a real implementation, you would:
        # 1. Look up the participant by phone number
        # 2. Determine what they're responding to (comm preference, question, plan feedback)
        # 3. Process the response accordingly
        
        logger.info(f"Received SMS from {From}: {Body}")
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/email")
async def email_webhook(from_email: str = None, subject: str = None, body: str = None):
    """Webhook for receiving email responses from participants."""
    try:
        if not from_email or not body:
            raise HTTPException(status_code=400, detail="Missing from_email or body parameters")
        
        # Similar to SMS webhook, in a real implementation you would process this appropriately
        
        logger.info(f"Received email from {from_email}: {subject}")
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing email webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Run the application with command line arguments."""
    parser = argparse.ArgumentParser(description="Group Activity Planning AI Agent")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
