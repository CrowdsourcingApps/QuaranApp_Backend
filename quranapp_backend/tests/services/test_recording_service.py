from src.dal.enums import RiwayahEnum, PublisherEnum
from src.dal.models import Recording, AyahPart
from src.models import AyahPartSearch
from src.services import ayah_parts
from src.services.recordings import create_recording, get_recording_by_id, delete_recording, share_recording, \
    get_shared_with_me_recordings, get_my_recordings, get_available_recordings


class TestRecordingService:
    saved_recording: Recording | None = None
    audio_url: str = "https://example.com/audio.mp3"
    start_ayah_part: AyahPart | None = None
    end_ayah_part: AyahPart | None = None

    @classmethod
    def set_init_data(cls, db_session):
        if cls.start_ayah_part is not None and cls.end_ayah_part is not None:
            return

        cls.start_ayah_part = ayah_parts.get_ayah_part(
            db_session, AyahPartSearch(surah_number=1, ayah_in_surah_number=0, part_number=0),
            RiwayahEnum.QALOON, PublisherEnum.MADINA
        )
        cls.end_ayah_part = ayah_parts.get_ayah_part(
            db_session, AyahPartSearch(surah_number=1, ayah_in_surah_number=1, part_number=0),
            RiwayahEnum.QALOON, PublisherEnum.MADINA
        )

    def test_create_recording(self, db_session, user1):
        test_class = type(self)

        user_id = user1.id
        self.set_init_data(db_session)

        recording = create_recording(db_session, user_id, self.start_ayah_part, self.end_ayah_part, self.audio_url)
        # сохраняем рекординг в атрибут класса, а не в атрибут инстанса
        test_class.saved_recording = recording

        assert recording.user_id == user_id
        assert recording.start == self.start_ayah_part
        assert recording.end == self.end_ayah_part
        assert recording.audio_url == self.audio_url

    def test_get_recording_by_id(self, db_session):
        recording = get_recording_by_id(db_session, self.saved_recording.id)

        assert recording is not None
        assert recording.id == self.saved_recording.id
        assert recording.audio_url == self.saved_recording.audio_url
        assert recording.user_id == self.saved_recording.user_id

    def test_share_recording(self, db_session, user2):
        recording = share_recording(db_session, self.saved_recording.id, user2.id)

        assert recording is not None
        assert recording.recipient_id == user2.id
        assert len(get_shared_with_me_recordings(db_session, user2.id)) == 1

    def test_get_shared_with_me_recordings(self, db_session, user1, user2):
        assert len(get_shared_with_me_recordings(db_session, user1.id)) == 0
        assert len(get_shared_with_me_recordings(db_session, user2.id)) == 1

    def test_get_my_recordings(self, db_session, user1):
        recordings = get_my_recordings(db_session, user1.id)

        assert len(recordings) == 1
        assert recordings[0].id == self.saved_recording.id

    def test_get_available_recordings(self, db_session, user1, user2):
        user1_recordings = get_available_recordings(db_session, user1.id)
        user2_recordings = get_available_recordings(db_session, user1.id)

        assert len(user1_recordings) == 1
        assert len(user2_recordings) == 1
        assert user1_recordings[0].id == self.saved_recording.id
        assert user2_recordings[0].id == self.saved_recording.id

    def test_delete_recording(self, db_session, user2):
        delete_recording(db_session, self.saved_recording.id)
        recording = db_session.get(Recording, self.saved_recording.id)

        assert recording.is_deleted
        assert len(get_shared_with_me_recordings(db_session, user2.id)) == 0

        # Clear db
        db_session.delete(recording)
        db_session.commit()
