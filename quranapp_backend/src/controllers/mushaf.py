import uuid

from fastapi import APIRouter

from src.dal.enums import RiwayahEnum


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
