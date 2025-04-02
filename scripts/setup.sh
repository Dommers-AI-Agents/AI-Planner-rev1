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

# Check for Python
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.10 or newer."
    exit 1
fi

$PYTHON_CMD -c "import sys; min_version = (3, 10); current = sys.version_info[:2]; sys.exit(0 if current >= min_version else 1)" || {
    print_error "Python 3.10 or newer is required. Found $($PYTHON_CMD --version)"
    exit 1
}

print_status "Found $($PYTHON_CMD --version)"

# Create virtual environment
print_status "Creating Python virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Skipping dependency installation."
fi

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
if [ -f nginx-config.conf ]; then
    cp nginx-config.conf nginx/conf.d/default.conf
elif [ -f nginx-config ]; then
    cp nginx-config nginx/conf.d/default.conf
else
    # Create a default Nginx configuration file
    cat > nginx/conf.d/default.conf << EOL
server {
    listen 80;
    server_name planner.yourdomain.com;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name planner.yourdomain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI application
    location / {
        proxy_pass http://planner-api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_read_timeout 300s;
    }

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://planner-api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Webhooks for SMS/email have higher rate limits
    location /webhook/ {
        limit_req zone=api burst=100 nodelay;
        proxy_pass http://planner-api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Logging
    access_log /var/log/nginx/planner_access.log;
    error_log /var/log/nginx/planner_error.log;
}
EOL
fi
print_status "Nginx configuration set up. Edit nginx/conf.d/default.conf to customize."

# Ensure proper permissions
print_status "Setting proper permissions..."
chmod -R 755 .
chmod 644 .env
chmod -R 777 data  # SQLite needs write access

# Ask about running mode
print_status "Setup mode selection..."
echo "Do you want to run the application in:"
echo "1) Development mode (local Python with virtual environment)"
echo "2) Production mode (Docker containers)"
read -p "Enter your choice (1 or 2): " RUN_MODE

if [ "$RUN_MODE" = "1" ]; then
    # Development mode
    print_status "Setting up for development mode..."
    
    # Create a run script for development
    cat > run_dev.sh << EOL
#!/bin/bash
source venv/bin/activate
cd app
python main.py --reload
EOL
    chmod +x run_dev.sh
    
    print_status "Setup completed successfully!"
    print_status "To run the application in development mode:"
    print_status "  ./run_dev.sh"
    print_status "The API will be available at http://localhost:8000"
    print_status ""
    print_warning "IMPORTANT: Before using in development:"
    print_warning "1. Edit .env with your actual API keys"

elif [ "$RUN_MODE" = "2" ]; then
    # Production mode
    print_status "Setting up for production mode..."
    
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
else
    print_error "Invalid choice. Please run the script again and select 1 or 2."
    exit 1
fi

# Deactivate virtual environment
deactivate
