from pydantic import BaseModel

from src.models.professional_audio import ProfessionalAudio


class AudioResponse(BaseModel):
    audios: list[ProfessionalAudio]
