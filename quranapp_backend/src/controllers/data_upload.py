from fastapi import APIRouter, UploadFile, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency, api_key_dependency
from src.services import mushafs as mushafs_service


data_upload_router = APIRouter(
    prefix="/data-upload",
    tags=["data-upload"],
    dependencies=[api_key_dependency]
)


@data_upload_router.post("/ayah-parts")
def upload_ayah_parts_data(
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
