#!/bin/bash
echo "Setting up environment..."
python -m venv env
pip install -r requirements.txt
echo "Environment setup complete."