from fastapi import FastAPI, APIRouter
from pydantic import BaseModel


app = FastAPI()

# class ProfessionalAudio(BaseModel):
#     surahNumber: int
#     ayahInSurahNumber: int
#     url: str
#
class User(BaseModel):
    id: int
    alias: str
#
# class Partition(BaseModel):
#     surahNumber: int
#     ayahInSurahNumber: int
#     partNumber: int
#
# class Range(BaseModel):
#     start: Partition
#     end: Partition
#
# class AudioResponse(BaseModel):
#     audios: list[ProfessionalAudio]
#
#
# pro_audio_db = []

# Define user router
user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user_router.get("/{user_id}")
def get_user(user_id: int):
    return {"message": f"Get user with ID: {user_id}"}


@user_router.get("/find/{user_alias}")
def find_user(user_alias: str):
    return {"message": f"Find user with alias: {user_alias}"}


@user_router.post("/create")
def create_user(user: User):
    return {"message": "Add new user"}


# Define recording router
recordings_router = APIRouter(
    prefix="/recordings",
    tags=["recordings"]
)


@recordings_router.get("/")
def get_recordings():
    pass


@recordings_router.post("/upload")
def upload_recording():
    pass


@recordings_router.delete("/{recording_id}")
def delete_recording(recording_id):
    pass


@recordings_router.post("/{recording_id}/share")
def share_recording(recording_id):
    pass


# Include routers in the app
app.include_router(user_router)
app.include_router(recordings_router)

