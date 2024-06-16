import sys
import os

# Add your project directory to the sys.path
project_home = '/home/rkale2/project3'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variable to tell Flask where your main app is
os.environ['FLASK_APP'] = 'app.py'

# Import the Flask app from your app.py
from app import app as application
