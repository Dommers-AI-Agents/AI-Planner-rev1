# Group Activity Planning AI Agent - Usage Guide

This guide explains how to use and deploy the Group Activity Planning AI Agent system.

## Overview

The Group Activity Planning AI Agent helps organize activities by:

1. Reaching out to participants with a link to a web interface to collect their preferences 
2. Analyzing everyone's preferences to create an optimal plan
3. Getting approval from the organizer via the web interface
4. Sharing the plan with all participants and collecting feedback through the web interface
5. Handling any necessary plan revisions

## System Requirements

- Ubuntu 20.04 or newer
- Python 3.10+
- Docker and Docker Compose
- At least 2GB RAM
- 10GB free disk space

## API Keys Required

To fully utilize the system, you'll need:

- Anthropic API key for Claude (for the AI agent)
- Twilio account for SMS notifications (initial contact and updates)
- SendGrid or similar for email notifications

## Installation

### 1. Clone the repository or copy all files to your server

```bash
git clone https://github.com/yourusername/activity-planner.git
cd activity-planner
```

### 2. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create the necessary directory structure
- Generate a template .env file
- Check for Docker and Docker Compose
- Set up Nginx configuration
- Build and start the Docker containers

### 3. Edit the .env file

Fill in your actual API keys in the .env file:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=your_email@example.com
BASE_URL=https://your-planner-domain.com
```

### 4. Configure your domain and SSL

Edit the Nginx configuration in `nginx/conf.d/default.conf` to use your actual domain. 
Place SSL certificates in `nginx/certs/` folder.

### 5. Restart the containers

```bash
docker-compose down
docker-compose up -d
```

## Using the API

### Create a Planning Session

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "organizer_name": "Jane Smith",
    "organizer_contact": "jane@example.com",
    "event_name": "Team Building Weekend",
    "participants": [
      {
        "name": "John Doe",
        "contact": "john@example.com"
      },
      {
        "name": "Alice Johnson",
        "contact": "+15551234567"
      }
    ]
  }'
```

This will:
1. Create a new planning session
2. Automatically send participants a link to the web interface for collecting preferences
3. Begin the preference collection process

### Check Session Status

```bash
curl -X GET http://localhost:8000/sessions/YOUR_SESSION_ID/status
```

### Generate Plan

Once enough preferences have been collected:

```bash
curl -X POST http://localhost:8000/plans/generate/YOUR_SESSION_ID
```

This will:
1. Generate a plan based on collected preferences
2. Send the plan to the organizer for approval via the web interface

### Additional Endpoints

The API provides several other endpoints for specific operations:

- `/preferences/comm-method` - Process communication preference for notifications
- `/preferences/response` - Process question responses from the web interface
- `/preferences/complete` - Mark preference collection as complete
- `/participant/questions` - Get all questions for a participant
- `/participant/send-reminder` - Send reminder to a participant
- `/plans/organizer-decision` - Record organizer's decision
- `/plans/participant-feedback` - Record participant feedback

## Web Interface URLs

The system provides web interfaces for both organizers and participants:

- Organizer Dashboard: `https://your-domain.com/organizer?session_id=YOUR_SESSION_ID`
- Participant Interface: `https://your-domain.com/participant?session_id=YOUR_SESSION_ID&participant_id=YOUR_PARTICIPANT_ID`

These links are automatically generated and sent to the respective users.

## Customization

### Modifying Questions

Edit the `base_questions` list in `preference_collector.py` to change the default questions.

### Tuning the Plan Generator

Adjust the parameters in the `create_plan` method of `plan_generator.py` to change how plans are generated.

### Design Considerations

- The system uses SQLite by default for simplicity. For production use with many concurrent users, consider switching to PostgreSQL.
- The code is modular, making it easy to replace components (e.g., replacing Twilio with another SMS provider).
- LLM prompts can be customized to get different conversation styles and plan generation strategies.

## Troubleshooting

### Viewing Logs

```bash
docker-compose logs -f
```

### Common Issues

1. **API Key Issues**: Ensure all API keys in .env file are correct and have necessary permissions.

2. **SMS/Email not being sent**: Verify your Twilio and SendGrid configurations.

3. **Database Errors**: Check that the data directory has proper write permissions.

## Support

For questions or issues, please open a ticket in the GitHub repository or contact support@yourdomain.com.