import io
import os
import shutil
import uuid
from collections import defaultdict

import torch
import torchaudio
from pydub import AudioSegment, exceptions as pydub_exceptions
from pydub.silence import split_on_silence
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from sqlalchemy.orm import Session, joinedload
from azure.core.exceptions import ResourceNotFoundError

from src.dal.models import Recording, AyahPart, Ayah
from src.dal.database import SessionLocal
from src.services import azure_blob_storage

temp_audio_chunks_dirname = "temp_audio_chunks"
if not os.path.isdir(temp_audio_chunks_dirname):
    os.mkdir(temp_audio_chunks_dirname)


# def defaultdict_factory():
#     return defaultdict(defaultdict_factory)


def get_all_ayah_parts_to_text_mapping(db_session: Session) -> dict:
    extended_ayah_parts = db_session.query(AyahPart).options(
        joinedload(AyahPart.ayah).joinedload(Ayah.mushaf), joinedload(AyahPart.text)
    ).all()

    # resulting_mapping = defaultdict(defaultdict_factory)
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

        resulting_mapping[mushaf_key][surah_number][ayah_number][extended_ayah_part.part_number] = ayah_part_text

    return resulting_mapping


db = SessionLocal()
ayah_parts_to_text_mapping = get_all_ayah_parts_to_text_mapping(db)


# def get_text_for_current_ayah_part(current_ayah_part: dict) -> str | None:
#     mushaf_key = f"{current_ayah_part['riwayah']}-{current_ayah_part['publisher']}"
#     surah_number = current_ayah_part['surah_number']
#     ayah_number = current_ayah_part['ayah_number']
#     part_number = current_ayah_part['part_number']
#
#     text = ayah_parts_to_text_mapping[mushaf_key][surah_number][ayah_number].get(part_number)
#     return text


# todo test
def get_all_texts_for_recording(start: dict, end: dict, recording_id: uuid.UUID) -> list[tuple]:
    current_ayah_part = start
    result_texts_with_ayah_part_info: list[tuple] = list()
    while current_ayah_part != end:

        # todo добавляю обработку на случай, если не нашли ая партов для такой-то суры и аята
        mushaf_key = f"{current_ayah_part['riwayah']}-{current_ayah_part['publisher']}"
        surah_number = current_ayah_part['surah_number']
        ayah_number = current_ayah_part['ayah_number']
        part_number = current_ayah_part['part_number']

        ayahs = ayah_parts_to_text_mapping[mushaf_key][surah_number]
        ayah_parts_texts = ayahs[ayah_number]
        text = ayah_parts_texts.get(part_number)

        if text is None:
            # Не включаю этот ая парт и текст в список текстов
            print(
                f"Text not found for the following ayah part, used in recording '{recording_id}':"
                f"Surah number={surah_number}, ayah number={ayah_number}, part number={part_number},"
                f" riwayah={current_ayah_part['riwayah']}, publisher={current_ayah_part['publisher']}"

            )

        else:
            result_texts_with_ayah_part_info.append((text, current_ayah_part))

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

    return result_texts_with_ayah_part_info


# Тут - пока не делаю фильтрацию по условию, что рекординг был зашерен и проверен
recordings = db.query(Recording).options(
    joinedload(Recording.start).joinedload(AyahPart.ayah).joinedload(Ayah.mushaf),
    joinedload(Recording.end).joinedload(AyahPart.ayah).joinedload(Ayah.mushaf),
).all()

processor = AutoProcessor.from_pretrained("tarteel-ai/whisper-base-ar-quran")
model = AutoModelForSpeechSeq2Seq.from_pretrained("tarteel-ai/whisper-base-ar-quran")

# Set device to GPU if available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
# Move model to GPU if available
model.to(device)

for recording in recordings:
    # # todo remove
    if str(recording.id) == "710e133a-dd65-4cbb-9cd6-763d16ce437b":
        recording_id = recording.id

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
            # пропускаю длинное аудио
            # if blob_name == "546A0FAD-58AB-4E51-8A5A-EFA03BF06D1C.m4a":
            #     continue

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

        audio_segment.export(f"audio_{recording_id}.wav", format="wav")

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

        start_ayah_part = recording.start
        start_ayah_part_info = {
            "riwayah": start_ayah_part.ayah.mushaf.riwayah,
            "publisher": start_ayah_part.ayah.mushaf.publisher,
            "surah_number": start_ayah_part.ayah.surah_number,
            "ayah_number": start_ayah_part.ayah.ayah_in_surah_number,
            "part_number": start_ayah_part.part_number
        }

        end_ayah_part = recording.end
        end_ayah_part_info = {
            "riwayah": end_ayah_part.ayah.mushaf.riwayah,
            "publisher": end_ayah_part.ayah.mushaf.publisher,
            "surah_number": end_ayah_part.ayah.surah_number,
            "ayah_number": end_ayah_part.ayah.ayah_in_surah_number,
            "part_number": end_ayah_part.part_number
        }

        recording_texts = get_all_texts_for_recording(start_ayah_part_info, end_ayah_part_info, recording_id)

        # Recognizing text in audio chunks
        for file_name in os.listdir(recording_chunks_dir_path):  # мб добавить "sorted"
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

            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

            print(f"Recording: {recording_id}, chunk: {file_name}, transcription: {transcription[0]}")

# # deleting temporary dirs for audio chunks
# for dir_name in os.listdir(temp_audio_chunks_dirname):
#     shutil.rmtree(os.path.join(temp_audio_chunks_dirname, dir_name))
