# Vercel entry point
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from web_app import app

# This is required for Vercel
if __name__ == "__main__":
    app.run()
