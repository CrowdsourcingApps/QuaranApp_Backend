import io
import json
import os
import re
import uuid
import shutil
from collections import defaultdict

import torch
import torchaudio
import nltk
# from nltk.corpus import stopwords
from pydub import AudioSegment, exceptions as pydub_exceptions
from pydub.silence import split_on_silence
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload, contains_eager
from azure.core.exceptions import ResourceNotFoundError

from src.dal.models import Recording, AyahPart, Ayah, AyahPartMarker, SharedRecording
from src.dal.database import SessionLocal
from src.services import azure_blob_storage

from dataset.utils import find_two_largest_values_and_indexes

nltk.download('punkt')

temp_audio_chunks_dirname = "temp_audio_chunks"
if not os.path.isdir(temp_audio_chunks_dirname):
    os.mkdir(temp_audio_chunks_dirname)
else:
    # deleting temporary dirs for audio chunks
    for dir_name in os.listdir(temp_audio_chunks_dirname):
        shutil.rmtree(os.path.join(temp_audio_chunks_dirname, dir_name))


def clean_text(arabic_text_str: str) -> str:
    # example: 'كَلَّا لَمَّا' -> 'كلا لما' (right to left)

    # Replace hamzat wasl (ٱ) and dagger alif (ٱ) with normal Alif (ا)
    arabic_text_str = arabic_text_str.replace('\u0671', 'ا').replace('\u0670', 'ا')

    # Define a regular expression pattern to match diacritic characters
    harakat_pattern = re.compile("""[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]""")

    # Use the sub() method to replace diacritic characters with an empty string
    text_without_harakat = re.sub(harakat_pattern, '', arabic_text_str)

    return text_without_harakat


def count_common_words_arabic(text1, text2) -> tuple:
    text1_cleaned = clean_text(text1)
    text2_cleaned = clean_text(text2)

    # Tokenize the sentences into words
    words_text1 = set(nltk.word_tokenize(text1_cleaned))
    words_text2 = set(nltk.word_tokenize(text2_cleaned))

    # Load Arabic stopwords
    # arabic_stopwords = set(stopwords.words('arabic'))

    # Find the intersection of the two sets to get common words
    common_words: set = words_text1.intersection(words_text2)

    # Count the number of common words
    count_common = len(common_words)

    return count_common, common_words


# count_common_words_arabic('فَأَنْبَتْنَا فِيهَا حَبًّا', 'فَأَنۢبَتْنَا فِيهَا حَبّاٗ')


def find_two_nearest_ayahs_for_chunk(recognized_text: str, recording_texts_all: list[str]):
    similarity_rates: list[float] = list()
    for i, ayah_part_text in enumerate(recording_texts_all):
        count_common, common_words = count_common_words_arabic(ayah_part_text, recognized_text)
        # similarity_rate = count_common / len(recognized_text) # original
        similarity_rate = count_common / len(nltk.word_tokenize(recognized_text))
        similarity_rates.append(similarity_rate)

    return find_two_largest_values_and_indexes(similarity_rates)


def get_all_ayah_parts_to_text_mapping(db_session: Session) -> dict:
    extended_ayah_parts = db_session.query(AyahPart).options(
        joinedload(AyahPart.ayah).joinedload(Ayah.mushaf), joinedload(AyahPart.text)
    ).all()

    resulting_mapping = dict()
    for extended_ayah_part in extended_ayah_parts:
        related_ayah: Ayah = extended_ayah_part.ayah
        mushaf_key = f"{related_ayah.mushaf.riwayah.value}-{related_ayah.mushaf.publisher.value}"
        if mushaf_key not in resulting_mapping:
            resulting_mapping[mushaf_key] = dict()
        surah_number = related_ayah.surah_number
        if surah_number not in resulting_mapping[mushaf_key]:
            resulting_mapping[mushaf_key][surah_number] = dict()
        ayah_number = related_ayah.ayah_in_surah_number
        if ayah_number not in resulting_mapping[mushaf_key][surah_number]:
            resulting_mapping[mushaf_key][surah_number][ayah_number] = dict()

        ayah_part_text = extended_ayah_part.text.text if extended_ayah_part.text else None

        resulting_mapping[mushaf_key][surah_number][ayah_number][extended_ayah_part.part_number] = {
            "text": ayah_part_text, "ayah_part_id": extended_ayah_part.id
        }

    return resulting_mapping


def get_markers_to_ayah_part_id_and_order_mapping(db_session: Session) -> dict:
    resulting_mapping = dict()
    markers = db_session.query(AyahPartMarker).all()
    for marker in markers:
        resulting_mapping[marker.id] = {"ayah_part_id": marker.ayah_part_id, "order": marker.order}
    return resulting_mapping


db = SessionLocal()
ayah_parts_to_text_mapping = get_all_ayah_parts_to_text_mapping(db)
markers_to_ayah_part_id_and_order_mapping = get_markers_to_ayah_part_id_and_order_mapping(db)


def get_all_texts_for_recording(start: dict, end: dict, recording_id: uuid.UUID) -> list[tuple]:
    current_ayah_part: dict = start
    result_texts_with_ayah_part_info: list[tuple] = list()
    while current_ayah_part != end:

        mushaf_key = f"{current_ayah_part['riwayah']}-{current_ayah_part['publisher']}"
        surah_number = current_ayah_part['surah_number']
        ayah_number = current_ayah_part['ayah_number']
        part_number = current_ayah_part['part_number']

        if surah_number not in ayah_parts_to_text_mapping[mushaf_key] or ayah_number not in \
                ayah_parts_to_text_mapping[mushaf_key][surah_number]:
            print(
                f"Recording '{recording_id}': ayah with surah number={surah_number}, ayah number={ayah_number} "
                f"not found. Skipping to the end of the range..."
            )
            current_ayah_part = end
            continue

        ayahs = ayah_parts_to_text_mapping[mushaf_key][surah_number]
        ayah_parts_texts = ayahs[ayah_number]
        # todo возможно добавить обработку на случай, если не нашли ая партов для этой суры и аята
        text = ayah_parts_texts[part_number].get("text")
        current_ayah_part_id = ayah_parts_texts[part_number].get("ayah_part_id")

        if text is None:
            print(
                f"Text not found for the following ayah part, used in recording '{recording_id}':"
                f"surah number={surah_number}, ayah number={ayah_number}, part number={part_number}, "
                f"riwayah={current_ayah_part['riwayah']}, publisher={current_ayah_part['publisher']}"

            )

        result_texts_with_ayah_part_info.append((text, {**current_ayah_part}, current_ayah_part_id))

        next_part_number = part_number + 1
        # Если есть следующий ая парт в том же аяте
        if next_part_number in ayah_parts_texts:
            current_ayah_part['part_number'] = next_part_number
            # Переходим к следующему ая парту
            continue

        next_ayah_number = ayah_number + 1
        # Если есть следующий аят в той же суре
        if next_ayah_number in ayahs:
            current_ayah_part['ayah_number'] = next_ayah_number
            continue

        next_surah_number = surah_number + 1
        current_ayah_part['surah_number'] = next_surah_number
        surah_ayahs = ayah_parts_to_text_mapping[mushaf_key].get(surah_number, list())
        if 0 in surah_ayahs:
            current_ayah_part['ayah_number'] = 0
        else:
            current_ayah_part['ayah_number'] = 1

    mushaf_key = f"{end['riwayah']}-{end['publisher']}"
    surah_number = end['surah_number']
    ayah_number = end['ayah_number']
    part_number = end['part_number']
    ayah_part_info = ayah_parts_to_text_mapping[mushaf_key][surah_number][ayah_number][part_number]
    end_ayah_text = ayah_part_info["text"]
    end_ayah_part_id = ayah_part_info["ayah_part_id"]

    if end_ayah_text is None:
        print(
            f"Text not found for the following ayah part, used in recording '{recording_id}':"
            f"surah number={surah_number}, ayah number={ayah_number}, part number={part_number}, "
            f"riwayah={end['riwayah']}, publisher={end['publisher']}"

        )
    result_texts_with_ayah_part_info.append((end_ayah_text, {**end}, end_ayah_part_id))

    return result_texts_with_ayah_part_info


# Тут - пока включаю те рекординги, которые не были проверены, и deleted-рекординги
shared_recordings_join_condition = and_(
    SharedRecording.recording_id == Recording.id, SharedRecording.is_reviewed == True
)
recordings = db.query(Recording).outerjoin(SharedRecording, shared_recordings_join_condition).options(
    joinedload(Recording.start).joinedload(AyahPart.ayah).joinedload(Ayah.mushaf),
    joinedload(Recording.end).joinedload(AyahPart.ayah).joinedload(Ayah.mushaf),
    joinedload(Recording.mistakes),
    contains_eager(Recording.shares)
).all()

processor = AutoProcessor.from_pretrained("tarteel-ai/whisper-base-ar-quran")
model = AutoModelForSpeechSeq2Seq.from_pretrained("tarteel-ai/whisper-base-ar-quran")

# Set device to GPU if available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
# Move model to GPU if available
model.to(device)

results = list()
ayah_parts_with_incorrect_markers = set()
all_recordings_count = db.query(Recording).count()
counter_initial_recordings = 0
counter_dataset_recordings = 0

for recording in recordings:
        recording_id = recording.id
        counter_initial_recordings += 1

        # loading audio file from Azure
        blob_name: str = recording.audio_url.split("/")[-1]
        try:
            file_bytes = azure_blob_storage.container_client.download_blob(blob_name).readall()
        except ResourceNotFoundError:
            print(f"Could not load audio for recording '{recording_id}': file not found. File name: '{blob_name}'")
            continue

        print(f"Downloaded audio file '{blob_name}' for recording '{recording_id}'")

        file_contents = io.BytesIO(file_bytes)
        audio_segment = None

        try:
            if blob_name.endswith(".mp4"):
                audio_segment = AudioSegment.from_file(file_contents, format="mp4")

            elif blob_name.endswith(".m4a"):
                audio_segment = AudioSegment.from_file(file_contents, format="m4a")

            elif blob_name.endswith(".mp3"):
                audio_segment = AudioSegment.from_mp3(file_contents)

            else:
                print(f"Unsupported extension, filename: {blob_name}")
                continue

        except pydub_exceptions.CouldntDecodeError as e:
            print(f"Could not read audio file '{blob_name}' for recording '{recording_id}', skipping...")
            continue

        # audio_segment.export(f"audio_{recording_id}.wav", format="wav")

        # Splitting audio based on silence
        audio_chunks = split_on_silence(audio_segment, min_silence_len=500, silence_thresh=-36)

        if not audio_chunks:
            print(f"Audio for recording '{recording_id}' seems to be too quiet, skipping...")
            continue

        recording_chunks_dir_path = os.path.join(temp_audio_chunks_dirname, f"chunks_recording_{recording_id}")
        os.mkdir(recording_chunks_dir_path)

        for i, audio_chunk in enumerate(audio_chunks):
            chunk_filepath = os.path.join(recording_chunks_dir_path, f"chunk{i}.wav")
            audio_chunk.export(chunk_filepath, format="wav")

        recording_reviewers = [recording_share.recipient_id for recording_share in recording.shares]
        is_recording_reviewed = True if recording_reviewers else False

        start_ayah_part = recording.start
        start_ayah_part_info = {
            "riwayah": start_ayah_part.ayah.mushaf.riwayah.value,
            "publisher": start_ayah_part.ayah.mushaf.publisher.value,
            "surah_number": start_ayah_part.ayah.surah_number,
            "ayah_number": start_ayah_part.ayah.ayah_in_surah_number,
            "part_number": start_ayah_part.part_number
        }

        end_ayah_part = recording.end
        end_ayah_part_info = {
            "riwayah": end_ayah_part.ayah.mushaf.riwayah.value,
            "publisher": end_ayah_part.ayah.mushaf.publisher.value,
            "surah_number": end_ayah_part.ayah.surah_number,
            "ayah_number": end_ayah_part.ayah.ayah_in_surah_number,
            "part_number": end_ayah_part.part_number
        }

        recording_texts_to_ayah_parts: list[tuple] = get_all_texts_for_recording(
            start_ayah_part_info, end_ayah_part_info, recording_id
        )
        filtered_recording_texts_to_ayah_parts = list(filter(lambda x: x[0] is not None, recording_texts_to_ayah_parts))
        print(
            f"Recording '{recording_id}': collected {len(recording_texts_to_ayah_parts)} ayah parts for a range, "
            f"with {len(filtered_recording_texts_to_ayah_parts)} of them containing text"
        )
        recording_texts = [text_to_ayah_part[0] for text_to_ayah_part in filtered_recording_texts_to_ayah_parts]
        if not recording_texts:
            print(f"Recording '{recording_id}': did not find any associated texts, skipping...")
            continue

        ayah_part_ids_to_texts_mapping = {
            ayah_part_info[2]: ayah_part_info[0] for ayah_part_info in filtered_recording_texts_to_ayah_parts
        }

        # текущая структура:
        # {ayah_part_id: {reviewer_id: {word_errors: {word: [error type 1, error type 2]}}}

        # Mapping errors to ayah parts
        ayah_parts_to_errors_mapping = defaultdict(dict)
        for error in recording.mistakes:
            ayah_part_and_order_info = markers_to_ayah_part_id_and_order_mapping[error.start_marker_id]
            ayah_part_id = ayah_part_and_order_info["ayah_part_id"]
            order = ayah_part_and_order_info["order"]

            ayah_part_text = ayah_part_ids_to_texts_mapping.get(ayah_part_id)
            if ayah_part_text is None:
                print(f"Recording '{recording_id}': could not map recording error '{error.id}' to word, text is empty")
                continue

            try:
                word_with_error = ayah_part_text.split(" ")[order]
            except IndexError:
                # Маркеры не соответствуют разбиению на слова; маркеров больше, чем должно быть для текущего текста
                ayah_parts_with_incorrect_markers.add(ayah_part_id)
                print(
                    f"Recording '{recording_id}': could find word by index {order} in text {ayah_part_text} "
                    f"for ayah part '{ayah_part_id}', seems markers are incorrect, skipping current recording error..."
                )
            else:
                ayah_part_errors = ayah_parts_to_errors_mapping[ayah_part_id]
                commentator_id = error.commentator_id
                if commentator_id not in ayah_part_errors:
                    ayah_part_errors[commentator_id] = dict()
                if word_with_error not in ayah_part_errors[commentator_id]:
                    ayah_part_errors[commentator_id][word_with_error] = set()
                ayah_part_errors[commentator_id][word_with_error].add(error.mistake_type.value)

        counter_dataset_recordings += 1

        # Counters for chunks: for chunks that we could not map to ayah part and for all chunks
        chunks_with_found_ayah_part = 0
        chunks_all = 0

        # Recognizing text in audio chunks, mapping audio chunk to ayah part based on text similarity
        for file_name in sorted(
                os.listdir(recording_chunks_dir_path),
                key=lambda x: int(x.removeprefix("chunk").split(".")[0])
        ):
            file_path = os.path.join(recording_chunks_dir_path, file_name)

            waveform, sample_rate = torchaudio.load(file_path)

            # Resample the waveform to the desired sampling rate
            resample_transform = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resample_transform(waveform)

            # Ensure that the waveform has only one channel (mono) and convert to NumPy array
            waveform = waveform.mean(dim=0, keepdim=True)
            waveform_np = waveform.numpy()

            # Tokenize and transcribe the audio
            sampling_rate = 16000
            input_features = processor(waveform_np, sampling_rate=sampling_rate, return_tensors="pt").input_features

            # Move input features to GPU
            input_features = input_features.to(device)

            # Generate transcription on GPU
            predicted_ids = model.generate(input_features)

            # Move back to CPU for decoding
            predicted_ids = predicted_ids.to("cpu")

            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

            print(f"Recording: {recording_id}, chunk: {file_name}, transcription: {transcription}")
            chunks_all += 1

            if not transcription:
                print(
                    f"Recording: '{recording_id}': recognized text for  chunk '{file_name}' is empty, skipping chunk..."
                )
                chunk_result = {
                    "file_name": os.path.join(recording_chunks_dir_path, file_name),
                    "recording_id": str(recording_id),
                    "riwayah": "undefined",
                    "surah": "undefined",
                    "ayah": "undefined",
                    "text": "undefined",
                    "errors": {},
                    "mushaf_publisher": "undefined",
                    "reviewer_id": "undefined" if is_recording_reviewed else "not reviewed"
                }
                results.append(chunk_result)
                continue

            most_similar_ind, second_similar_ind, similarity_rate, second_similarity_rate = find_two_nearest_ayahs_for_chunk(
                recognized_text=transcription, recording_texts_all=recording_texts
            )

            if similarity_rate == 0:
                print(
                    f"Recording '{recording_id}': did not find closest ayah part for chunk '{file_name}', "
                    f"transcription '{transcription}'"
                )
                chunk_result = {
                    "file_name": os.path.join(recording_chunks_dir_path, file_name),
                    "recording_id": str(recording_id),
                    "riwayah": "undefined",
                    "surah": "undefined",
                    "ayah": "undefined",
                    "text": "undefined",
                    "errors": {},
                    "mushaf_publisher": "undefined",
                    "reviewer_id": "undefined" if is_recording_reviewed else "not reviewed"
                }

            else:
                chunks_with_found_ayah_part += 1
                mapped_ayah_part = filtered_recording_texts_to_ayah_parts[most_similar_ind]
                print(
                    f"Recording '{recording_id}': resulting ayah part "
                    f"for chunk '{file_name}' is {mapped_ayah_part}"
                )
                mapped_ayah_part_text = mapped_ayah_part[0]
                mapped_ayah_part_info = mapped_ayah_part[1]
                mapped_ayah_part_id = mapped_ayah_part[2]

                errors_by_reviewers_info = list()

                if is_recording_reviewed:
                    overall_errors_info = ayah_parts_to_errors_mapping[mapped_ayah_part_id]
                    for reviewer_id in recording_reviewers:
                        errors_by_reviewer = overall_errors_info.get(reviewer_id, {})
                        formatted_errors_by_reviewer = {
                            word: list(errors_set) for word, errors_set in errors_by_reviewer.items()
                        }
                        errors_by_reviewers_info.append((reviewer_id, formatted_errors_by_reviewer))
                else:
                    errors_by_reviewers_info.append(("not reviewed", {}))

                for errors_marked_by_reviewer in errors_by_reviewers_info:
                    chunk_result = {
                        "file_name": os.path.join(recording_chunks_dir_path, file_name),
                        "recording_id": str(recording_id),
                        "riwayah": mapped_ayah_part_info["riwayah"],
                        "surah": str(mapped_ayah_part_info["surah_number"]),
                        "ayah": str(mapped_ayah_part_info["ayah_number"]),
                        "text": mapped_ayah_part_text,
                        "errors": errors_marked_by_reviewer[1],
                        "mushaf_publisher": mapped_ayah_part_info["publisher"],
                        "reviewer_id": errors_marked_by_reviewer[0]
                    }
                    results.append(chunk_result)

        print(f"Found ayah parts for {chunks_with_found_ayah_part} out of {chunks_all} audio chunks")

if ayah_parts_with_incorrect_markers:
    ayah_part_ids = [str(ayah_part_id) for ayah_part_id in ayah_parts_with_incorrect_markers]
    print(f"There are incorrect markers for ayah parts: {', '.join(ayah_part_ids)}")

print(
    f"Collected {counter_dataset_recordings} out of initial {counter_initial_recordings} to a dataset. "
    f"Overall amount of recordings in a database: {all_recordings_count}"
)

with open("metadata.jsonl", "w") as f:
    for result in results:
        f.write(json.dumps(result))
        f.write("\n")
