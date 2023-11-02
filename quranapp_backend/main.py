import sys
import os
import src.startup as startup
from fastapi import FastAPI
from src.controllers import recordings, users, settings

print(os.getcwd())

app = FastAPI()

# Include routers in the app
app.include_router(users)
app.include_router(recordings)
app.include_router(settings)

startup.apply_migrations()
