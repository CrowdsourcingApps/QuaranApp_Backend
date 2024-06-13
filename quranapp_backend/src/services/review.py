import uuid

from sqlalchemy.orm import Session, joinedload

from src.dal.models import RecordingMistake
from src.models import Mistake, MistakeReviewInformation, MistakeMarkerInformation


def upload_review(
        db: Session, recording_id: uuid.UUID, commentator_id: str, mistakes: list[Mistake]
) -> None:
    (db.query(RecordingMistake)
     .filter_by(recording_id=recording_id, commentator_id=commentator_id)
     .delete(synchronize_session=False))

    db.commit()

    mistakes_to_load = [
        RecordingMistake(
            commentator_id=commentator_id,
            recording_id=recording_id,
            start_marker_id=mistake.start_marker_id,
            end_marker_id=mistake.end_marker_id,
            mistake_type=mistake.type
        ) for mistake in mistakes]

    db.add_all(mistakes_to_load)
    db.commit()


def get_reviews(
        db: Session, recording_id: uuid.UUID
) -> list[MistakeMarkerInformation]:
    recording_mistakes = db.query(RecordingMistake).filter_by(
        recording_id=recording_id
    ).options(
        joinedload(RecordingMistake.commentator)
    ).all()

    result = {}
    for mistake in recording_mistakes:
        if (mistake.start_marker_id, mistake.end_marker_id,) in result:
            for mistake_type in result[(mistake.start_marker_id, mistake.end_marker_id,)].mistakes:
                if mistake_type.type == mistake.mistake_type:
                    mistake_type.commentators.append(mistake.commentator.alias)
                    break
            result[(mistake.start_marker_id, mistake.end_marker_id,)].mistakes.append(
                MistakeReviewInformation(
                    type=mistake.mistake_type,
                    commentators=[mistake.commentator.alias])
            )
        else:
            result[(mistake.start_marker_id, mistake.end_marker_id,)] =\
                MistakeMarkerInformation(
                    start_marker_id=mistake.start_marker_id,
                    end_marker_id=mistake.end_marker_id,
                    mistakes=[
                        MistakeReviewInformation(
                            type=mistake.mistake_type,
                            commentators=[mistake.commentator.alias])
                    ]
                )

    return list(result.values())
