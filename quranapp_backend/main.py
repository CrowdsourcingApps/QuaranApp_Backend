import sys
import os
import src.startup as startup
from fastapi import FastAPI
from src.controllers import recordings, users, settings

print(os.getcwd())

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

app = FastAPI()

# Include routers in the app
app.include_router(users)
app.include_router(recordings)
app.include_router(settings)

startup.apply_migrations()
