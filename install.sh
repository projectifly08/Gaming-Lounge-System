#!/bin/bash
echo "Installing Gaming Lounge Management System..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up environment variables
echo "Setting up environment variables..."
cp .env.example .env
echo "Please edit the .env file with your database connection details."
echo "IMPORTANT: You need to set the correct MySQL credentials in the .env file."
echo "The default credentials may not work with your MySQL setup."
echo ""
read -p "Press Enter to open the .env file for editing..." nothing
${EDITOR:-nano} .env
echo ""
echo "After editing the .env file, press Enter to continue with database initialization..."
read nothing

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_admin.sh run_launcher.sh

# Initialize database
echo "Initializing database..."
python -m src.database.init_db
if [ $? -ne 0 ]; then
    echo ""
    echo "Database initialization failed. Please check your MySQL credentials in the .env file."
    echo "Make sure your MySQL server is running and the credentials are correct."
    echo ""
    exit 1
fi

echo "Installation complete!"
echo "To start the admin panel, run: ./run_admin.sh"
echo "To start the game launcher, run: ./run_launcher.sh" 