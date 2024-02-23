from src.services.surahs import get_all_surahs


def test_get_all_surahs(db_session):
    surahs = get_all_surahs(db_session)
    assert len(surahs) == 114
