# Group Activity Planning AI Agent

An intelligent AI agent that helps coordinate group activities by collecting participant preferences through a web interface and generating optimal plans.

## Features

- Streamlined web-based preference collection
- One-time notification system (SMS, email) with web links
- Intuitive participant and organizer dashboards
- Intelligent preference analysis
- Smart plan generation based on collected preferences
- Simplified approval and feedback workflow

## Requirements

- Python 3.10+
- Docker and Docker Compose
- Anthropic API key
- Twilio account (for SMS notifications)
- SendGrid or similar (for email notifications)

## Quick Start

1. Clone this repository
2. Run `./scripts/setup.sh`
3. Edit the `.env` file with your API keys
4. Update the Nginx configuration with your domain
5. Run `docker-compose up -d`

See the [Usage Guide](USAGE.md) for more detailed instructions.

## License

[MIT](LICENSE)