#!/bin/bash

# Group Activity Planning AI Agent Setup Script
# This script sets up the environment for the planner application

set -e  # Exit on error

# Print colored messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$(id -u)" -eq 0 ]; then
    print_warning "Running as root is not recommended. Consider running as a regular user with sudo privileges."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directory structure
print_status "Creating directory structure..."
mkdir -p data
mkdir -p nginx/conf.d
mkdir -p nginx/certs
mkdir -p nginx/logs

# Create .env file for environment variables
print_status "Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOL
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=your_email@example.com

# Database settings
DB_PATH=./data/planner.db
EOL
    print_status ".env file created. Please edit it with your API keys."
else
    print_warning ".env file already exists. Skipping."
fi

# Check for Docker and Docker Compose
print_status "Checking for Docker and Docker Compose..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose not found. Attempting to install..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
fi

# Copy Nginx configuration
print_status "Setting up Nginx configuration..."
cp nginx-config.conf nginx/conf.d/default.conf
print_status "Nginx configuration copied. Edit nginx/conf.d/default.conf to customize."

# Ensure proper permissions
print_status "Setting proper permissions..."
chmod -R 755 .
chmod 644 .env
chmod -R 777 data  # SQLite needs write access

# Build and start the containers
print_status "Building and starting containers..."
docker-compose build
docker-compose up -d

print_status "Setup completed successfully!"
print_status "The API is now running at http://localhost:8000"
print_status "To view logs: docker-compose logs -f"
print_status "To stop the service: docker-compose down"
print_status ""
print_warning "IMPORTANT: Before using in production:"
print_warning "1. Edit .env with your actual API keys"
print_warning "2. Update nginx/conf.d/default.conf with your domain"
print_warning "3. Add SSL certificates to nginx/certs/"
print_warning "4. Edit 'planner.yourdomain.com' in nginx config to your actual domain"
