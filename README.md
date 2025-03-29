# Group Activity Planning AI Agent

An intelligent AI agent that helps coordinate group activities by collecting participant preferences and generating optimal plans.

## Features

- Multi-channel communication (SMS, email, voice calls)
- Intelligent preference collection
- Adaptive questioning
- Smart plan generation based on collected preferences
- Approval workflow
- Feedback management

## Requirements

- Python 3.10+
- Docker and Docker Compose
- Anthropic API key
- Twilio account (for SMS and voice)
- SendGrid or similar (for email)

## Quick Start

1. Clone this repository
2. Run \`./scripts/setup.sh\`
3. Edit the \`.env\` file with your API keys
4. Update the Nginx configuration with your domain
5. Run \`docker-compose up -d\`

See the [Usage Guide](USAGE.md) for more detailed instructions.

## License

[MIT](LICENSE)
