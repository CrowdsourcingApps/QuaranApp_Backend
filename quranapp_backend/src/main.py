import sys
import os
from fastapi import FastAPI
from src.controllers import recordings, users, settings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

app = FastAPI()

# Include routers in the app
app.include_router(users)
app.include_router(recordings)
app.include_router(settings)
