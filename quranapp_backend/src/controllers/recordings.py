from fastapi import APIRouter

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
