import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload, contains_eager
from starlette import status

from src.dal.models import MushafPage, Ayah, AyahPart, AyahPartText, ReciterAudio
from src.mappers import ayah_part_mapper
from src.models import MushafPageDetails, PagesRangeRequest, RangeStartAndEndPages


def get_pages_by_mushaf_id(db: Session, mushaf_id: uuid.UUID) -> list[MushafPage]:
    return db.query(MushafPage).filter_by(mushaf_id=mushaf_id).order_by(MushafPage.index).all()


def get_ayah_parts_and_markers_by_page_id(db: Session, page_id: uuid.UUID) -> MushafPageDetails:
    # contains_eager использую, чтобы иметь возможность фильтровать после JOIN'а, и при этом иметь доступ
    # к атрибутам Aayh. Документация: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#routing-explicit-joins-statements-into-eagerly-loaded-collections
    ayah_parts = db.query(AyahPart).filter_by(mushaf_page_id=page_id).join(Ayah, Ayah.id == AyahPart.ayah_id).options(
        contains_eager(AyahPart.ayah).joinedload(Ayah.mushaf),
        joinedload(AyahPart.markers),
        joinedload(AyahPart.text).joinedload(AyahPartText.reciter_audios).joinedload(ReciterAudio.reciter)
    ).order_by(Ayah.surah_number, Ayah.ayah_in_surah_number).all()

    return ayah_part_mapper.map_to_page_details(page_id=page_id, ayah_parts=ayah_parts)


def get_first_and_last_pages_for_range(db: Session, mushaf_id: uuid.UUID, request: PagesRangeRequest) -> RangeStartAndEndPages:
    start_ayah_part = (db.query(AyahPart)
                       .filter_by(part_number=0)
                       .join(Ayah, Ayah.id == AyahPart.ayah_id)
                       .filter(Ayah.mushaf_id == mushaf_id, Ayah.surah_number == request.start_surah_number, Ayah.ayah_in_surah_number == request.start_ayah_in_surah_number)
                       .options(joinedload(AyahPart.mushaf_page))
                       .first())

    end_ayah_part = (db.query(AyahPart)
                       .filter_by(part_number=0)
                       .join(Ayah, Ayah.id == AyahPart.ayah_id)
                       .filter(Ayah.mushaf_id == mushaf_id, Ayah.surah_number == request.end_surah_number, Ayah.ayah_in_surah_number == request.end_ayah_in_surah_number)
                       .options(joinedload(AyahPart.mushaf_page))
                       .first())

    if not start_ayah_part or not end_ayah_part:
        raise HTTPException(detail="Ayahs not found", status_code=status.HTTP_404_NOT_FOUND)

    if not start_ayah_part.mushaf_page.index or not end_ayah_part.mushaf_page.index:
        raise HTTPException(detail="Page for Ayah not found", status_code=status.HTTP_404_NOT_FOUND)

    return RangeStartAndEndPages(
        start_page_id=start_ayah_part.mushaf_page_id,
        start_page_index=start_ayah_part.mushaf_page.index,
        end_page_id=end_ayah_part.mushaf_page_id,
        end_page_index=end_ayah_part.mushaf_page.index
    )
