import uuid

from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, HTTPException, status
from pydantic import ValidationError

from src.dal.enums import RiwayahEnum
from src.services import mushafs as mushafs_service
from src.controllers.dependencies import db_session_dependency


mushaf_router = APIRouter(
    prefix="/mushaf",
    tags=["mushaf"]
)


@mushaf_router.get("/pages/{riwayah}/{publisher}")
def get_mushaf_pages(riwayah: RiwayahEnum, publisher: str):
    # RETURN
    # Sorted List of MushafPages
    pass


@mushaf_router.get("/page/{id}")
def get_page(id: uuid.UUID):
    # RETURN
    # AyahParts / Markers
    pass


@mushaf_router.get("/surahs/{riwayah}/{publisher}")
def get_surahs(riwayah: RiwayahEnum, publisher: str):
    # RETURN
    # Sorted by surah number List of (Surah, pageIndex)
    pass


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
