import uuid

from pydantic import BaseModel

from src.dal.enums import MistakeType


class Mistake(BaseModel):
    start_marker_id: uuid.UUID
    end_marker_id: uuid.UUID
    type: MistakeType

    def __eq__(self, other):
        if isinstance(other, Mistake):
            return (self.start_marker_id == other.start_marker_id
                    and self.end_marker_id == other.end_marker_id
                    and self.type == other.type)
        return False


class MistakesRequest(BaseModel):
    mistakes: list[Mistake]


class MistakeReviewInformation(BaseModel):
    type: MistakeType
    commentators: list[str]


class MistakeMarkerInformation(BaseModel):
    start_marker_id: uuid.UUID
    end_marker_id: uuid.UUID
    mistakes: list[MistakeReviewInformation]
