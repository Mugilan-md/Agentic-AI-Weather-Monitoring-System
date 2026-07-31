import os
import sys

# Project root path resolution for Vercel Serverless Function
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

app = app
handler = app
