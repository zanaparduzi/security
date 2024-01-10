#!/bin/bash

# Replace these variables with your VM credentials and project details
VM_USER="admin"
VM_ADDRESS="139.124.86.169"
PROJECT_DIRECTORY="secu"

# Stop the existing application if it's running
pkill -f "python app.py"

# Update code from GitLab repository
git pull gitlab master

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Copy the project files to the VM using SSH and rsync
rsync -avz --exclude='.git/' ./ "$VM_USER@$VM_ADDRESS:$PROJECT_DIRECTORY"

# Restart the application on the VM
ssh "$VM_USER@$VM_ADDRESS" "cd $PROJECT_DIRECTORY && nohup python app.py &"
