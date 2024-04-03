import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency
from src.dal.enums import RiwayahEnum, PublisherEnum
from src.models import MushafPage, SurahInMushaf, MushafPageDetails
from src.services import surahs_service, mushafs_service, mushaf_pages_service

mushaf_router = APIRouter(
    prefix="/mushaf",
    tags=["mushaf"]
)


@mushaf_router.get("/pages/{riwayah}/{publisher}", response_model=list[MushafPage])
def get_mushaf_pages(riwayah: RiwayahEnum, publisher: PublisherEnum, db: Session = db_session_dependency):
    mushaf = mushafs_service.get_mushaf_if_exists(db=db, riwayah=riwayah, publisher=publisher)
    if not mushaf:
        raise HTTPException(detail="Mushaf not found", status_code=status.HTTP_404_NOT_FOUND)
    return mushaf_pages_service.get_pages_by_mushaf_id(db=db, mushaf_id=mushaf.id)


@mushaf_router.get("/page/{page_id}", response_model=MushafPageDetails)
def get_page_details(page_id: uuid.UUID, db: Session = db_session_dependency):
    return mushaf_pages_service.get_ayah_parts_and_markers_by_page_id(db=db, page_id=page_id)


@mushaf_router.get("/surahs/{riwayah}/{publisher}", response_model=list[SurahInMushaf])
def get_surahs(riwayah: RiwayahEnum, publisher: PublisherEnum, db: Session = db_session_dependency) -> list[SurahInMushaf]:
    mushaf = mushafs_service.get_mushaf_if_exists(db=db, riwayah=riwayah, publisher=publisher)
    if not mushaf:
        raise HTTPException(detail="Mushaf not found", status_code=status.HTTP_404_NOT_FOUND)
    return surahs_service.get_surahs_in_mushaf(db=db, mushaf_id=mushaf.id)
