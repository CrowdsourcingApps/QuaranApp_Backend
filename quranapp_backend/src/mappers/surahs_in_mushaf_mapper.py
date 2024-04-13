import uuid

from src.dal.models import SurahInMushaf as SurahInMushafDal
from src.models import SurahInMushaf


def map_surahs_in_mushaf(mushaf_id: uuid.UUID, surahs_in_mushaf_dal: list[SurahInMushafDal]) -> list[SurahInMushaf]:
    result = []
    for surah_in_mushaf in surahs_in_mushaf_dal:
        ayahs = set()

        for ayah in surah_in_mushaf.surah.ayahs:
            if ayah.mushaf_id == mushaf_id:
                ayahs.add(ayah.ayah_in_surah_number)

        result.append(SurahInMushaf(
            first_page_id=surah_in_mushaf.first_page_id,
            first_page_index=surah_in_mushaf.mushaf_page.index,
            surah_number=surah_in_mushaf.surah_number,
            surah_title=surah_in_mushaf.surah.title_eng,
            ayahs_in_surah=sorted(list(ayahs))
        ))

    return result
