from enum import Enum


class RiwayahEnum(Enum):
    HAFS = "Hafs"
    QALOON = "Qaloon"


class PublisherEnum(Enum):
    MADINA = "Madina"
    JAWAMEE = "Jawamee"


class MistakeType(Enum):
    WORDING = "Wording"
    LETTERS = "Letters"
    TASHKEEL = "Tashkeel"
    TAJWEED = "Tajweed"
