import os

import pytest
from sqlalchemy.orm import joinedload

from src.services import mushafs as mushafs_service
from src.dal.models import AyahPart, AyahPartMarker, AyahPartText, Ayah, MushafPage
from src.dal.enums import RiwayahEnum, PublisherEnum

ayah_parts_data_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "ayah_parts_upload")
page_images_data_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "page_images_upload")


class TestAyahPartsDataUploader:
    def test_data_upload(self, db_session):
        ayahs_count = db_session.query(Ayah).count()
        ayah_parts_count = db_session.query(AyahPart).count()
        ayah_part_texts_count = db_session.query(AyahPartText).count()
        mushaf_pages_count = db_session.query(MushafPage).count()
        ayah_part_markers_count = db_session.query(AyahPartMarker).count()

        ayah_parts_data_uploader = mushafs_service.AyahPartsDataUploader(db=db_session)
        with open(os.path.join(ayah_parts_data_directory, "ayah_parts_page_5000.json")) as f:
            ayah_parts_data_uploader.save_data_from_ayah_parts_file(f)

        new_ayahs_count = db_session.query(Ayah).count()
        new_ayah_parts_count = db_session.query(AyahPart).count()
        new_ayah_part_texts_count = db_session.query(AyahPartText).count()
        new_mushaf_pages_count = db_session.query(MushafPage).count()
        new_ayah_part_markers_count = db_session.query(AyahPartMarker).count()

        assert new_ayahs_count == ayahs_count + 8
        assert new_ayah_parts_count == ayah_parts_count + 9
        assert new_ayah_part_texts_count == ayah_part_texts_count + 3  # 3 new unique texts
        assert new_mushaf_pages_count == mushaf_pages_count + 1
        assert new_ayah_part_markers_count > ayah_part_markers_count

    def test_data_upload_same_data(self, db_session):
        ayah_parts_count = db_session.query(AyahPart).count()
        mushaf_pages_count = db_session.query(MushafPage).count()
        ayah_part_markers_count = db_session.query(AyahPartMarker).count()

        ayah_parts_data_uploader = mushafs_service.AyahPartsDataUploader(db=db_session)
        with open(os.path.join(ayah_parts_data_directory, "ayah_parts_page_5000.json")) as f:
            ayah_parts_data_uploader.save_data_from_ayah_parts_file(f)

        new_ayah_parts_count = db_session.query(AyahPart).count()
        new_mushaf_pages_count = db_session.query(MushafPage).count()
        new_ayah_part_markers_count = db_session.query(AyahPartMarker).count()

        assert new_ayah_parts_count == ayah_parts_count
        assert new_mushaf_pages_count == mushaf_pages_count
        assert new_ayah_part_markers_count == ayah_part_markers_count

    def test_data_update(self, db_session):
        ayah_part_1 = db_session.query(AyahPart).filter(AyahPart.ayah.has(ayah_in_surah_number=1003)).options(
            joinedload(AyahPart.markers)
        ).first()
        ayah_part_2 = db_session.query(AyahPart).filter(AyahPart.ayah.has(ayah_in_surah_number=1005)).options(
            joinedload(AyahPart.text)
        ).first()

        assert len(ayah_part_1.markers) == 0
        assert ayah_part_2.text.text == "Test text data upload"

        ayah_parts_data_uploader = mushafs_service.AyahPartsDataUploader(db=db_session)
        with open(os.path.join(ayah_parts_data_directory, "ayah_parts_page_5000_updated.json")) as f:
            ayah_parts_data_uploader.save_data_from_ayah_parts_file(f)

        updated_ayah_part_1 = db_session.query(AyahPart).filter(AyahPart.ayah.has(ayah_in_surah_number=1003)).options(
            joinedload(AyahPart.markers)
        ).first()
        updated_ayah_part_2 = db_session.query(AyahPart).filter(AyahPart.ayah.has(ayah_in_surah_number=1005)).options(
            joinedload(AyahPart.text)
        ).first()

        assert len(updated_ayah_part_1.markers) == 5
        assert updated_ayah_part_2.text.text == "Test text data upload. Updated text"

    def test_data_upload_unexisting_surah(self, db_session):
        ayah_parts_count = db_session.query(AyahPart).count()
        ayah_part_texts_count = db_session.query(AyahPartText).count()

        ayah_parts_data_uploader = mushafs_service.AyahPartsDataUploader(db=db_session)
        with open(os.path.join(ayah_parts_data_directory, "ayah_parts_page_5000_unexisting_surah.json")) as f:
            with pytest.raises(mushafs_service.DataUploadException):
                ayah_parts_data_uploader.save_data_from_ayah_parts_file(f)

        new_ayah_parts_count = db_session.query(AyahPart).count()
        new_ayah_part_texts_count = db_session.query(AyahPartText).count()

        # No data should be saved if there is an error during data upload
        assert new_ayah_parts_count == ayah_parts_count
        assert new_ayah_part_texts_count == ayah_part_texts_count

    def test_data_upload_invalid_json(self, db_session):
        ayah_parts_data_uploader = mushafs_service.AyahPartsDataUploader(db=db_session)
        with open(os.path.join(ayah_parts_data_directory, "ayah_parts_json_invalid.json")) as f:
            with pytest.raises(mushafs_service.DataUploadException):
                ayah_parts_data_uploader.save_data_from_ayah_parts_file(f)


class PageImagesDataUploader:
    def test_data_upload(self, db_session):
        mushaf = mushafs_service.get_mushaf_if_exists(db_session, RiwayahEnum.QALOON, PublisherEnum.MADINA)
        if not mushaf:
            mushaf = mushafs_service.create_mushaf(db_session, RiwayahEnum.QALOON, PublisherEnum.MADINA)

        page_1 = db_session.query(MushafPage).filter_by(index=5000).first()
        if not page_1:
            db_page = MushafPage(index=5000, mushaf_id=mushaf.id)
            db_session.add(db_page)
            db_session.commit()

        assert page_1.light_mode_link is None and page_1.dark_mode_link is None

        page_images_data_uploader = mushafs_service.PageImagesDataUploader(db=db_session)
        with open(os.path.join(page_images_data_directory, "page_images_pages_5000_5001.json")) as f:
            page_images_data_uploader.save_data_from_page_images_file(f)

        db_session.refresh(page_1)
        assert page_1.light_mode_link is not None and page_1.dark_mode_link is not None

        # New page, created after data upload
        page_2 = db_session.query(MushafPage).filter_by(index=5000).first()
        assert page_2 is not None
        assert page_2.light_mode_link is not None and page_2.dark_mode_link is not None



