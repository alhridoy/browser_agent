#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Install Playwright browsers
python3 -m playwright install

# Create logs directory
mkdir -p logs

echo "Setup completed successfully!"
echo "To activate the virtual environment, run: source venv/bin/activate"
