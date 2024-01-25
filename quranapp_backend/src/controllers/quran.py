from fastapi import APIRouter

quran_router = APIRouter(
    prefix="/quran",
    tags=["quran"]
)


@quran_router.get("/surahs")
def get_surahs():
    # RETURN
    # List of Surah
    pass

