from pydantic import BaseModel
from src.models.professionalAudio import ProfessionalAudio


class AudioResponse(BaseModel):
    audios: list[ProfessionalAudio]