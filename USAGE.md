# Group Activity Planning AI Agent - Usage Guide

This guide explains how to use and deploy the Group Activity Planning AI Agent system.

## Overview

The Group Activity Planning AI Agent helps organize activities by:

1. Reaching out to participants to collect their preferences 
2. Analyzing everyone's preferences to create an optimal plan
3. Getting approval from the organizer
4. Sharing the plan with all participants and collecting feedback
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
- Twilio account for SMS and voice calls
- SendGrid or similar for email communications

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
2. Automatically reach out to participants asking for their preferred communication method
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
2. Send the plan to the organizer for approval

### Additional Endpoints

The API provides several other endpoints for specific operations:

- `/preferences/comm-method` - Process communication preference
- `/preferences/response` - Process question responses
- `/plans/organizer-decision` - Record organizer's decision
- `/plans/participant-feedback` - Record participant feedback

## Handling Incoming Messages

The system provides webhook endpoints for handling responses from participants:

- `/webhook/sms` - For SMS responses via Twilio
- `/webhook/email` - For email responses

You'll need to configure your Twilio and email services to forward responses to these endpoints.

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

2. **SMS/Voice not working**: Verify your Twilio phone number is properly configured for both SMS and voice capabilities.

3. **Database Errors**: Check that the data directory has proper write permissions.

## Support

For questions or issues, please open a ticket in the GitHub repository or contact support@yourdomain.com.
