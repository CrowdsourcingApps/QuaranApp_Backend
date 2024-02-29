import uuid

from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, HTTPException, status
from pydantic import ValidationError

from src.dal.enums import RiwayahEnum, PublisherEnum
from src.services import surahs_service, mushafs_service, mushaf_pages_service
from src.controllers.dependencies import db_session_dependency
from src.models.surah import SurahInMushaf

mushaf_router = APIRouter(
    prefix="/mushaf",
    tags=["mushaf"]
)


@mushaf_router.get("/pages/{riwayah}/{publisher}")
def get_mushaf_pages(riwayah: RiwayahEnum, publisher: PublisherEnum, db: Session = db_session_dependency):
    mushaf = mushafs_service.get_mushaf_if_exists(db=db, riwayah=riwayah, publisher=publisher)
    if not mushaf:
        raise HTTPException(detail="Mushaf not found", status_code=status.HTTP_404_NOT_FOUND)
    return mushaf_pages_service.get_pages_by_mushaf_id(db=db, mushaf_id=mushaf.id)


@mushaf_router.get("/page/{page_id}")
def get_page(page_id: uuid.UUID, db: Session = db_session_dependency):
    return mushaf_pages_service.get_ayah_parts_and_markers_by_page_id(db=db, page_id=page_id)


@mushaf_router.get("/surahs/{riwayah}/{publisher}", response_model=list[SurahInMushaf])
def get_surahs(riwayah: RiwayahEnum, publisher: PublisherEnum, db: Session = db_session_dependency) -> list[SurahInMushaf]:
    mushaf = mushafs_service.get_mushaf_if_exists(db=db, riwayah=riwayah, publisher=publisher)
    if not mushaf:
        raise HTTPException(detail="Mushaf not found", status_code=status.HTTP_404_NOT_FOUND)
    return surahs_service.get_surahs_in_mushaf(db=db, mushaf_id=mushaf.id)


@mushaf_router.post("/upload-mushaf-data")
def upload_mushaf_data(
        mushaf_file: UploadFile,
        db: Session = db_session_dependency
):
    if not mushaf_file.filename.endswith(".json"):
        raise HTTPException(detail="Mushaf file must have .json extension", status_code=status.HTTP_400_BAD_REQUEST)

    service = mushafs_service.MushafDataUploader(db=db)
    try:
        service.save_data_from_mushaf_file(mushaf_file.file)
    except ValidationError as e:
        raise HTTPException(detail=e.errors(), status_code=status.HTTP_400_BAD_REQUEST)
    except mushafs_service.DataUploadException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    finally:
        mushaf_file.file.close()
