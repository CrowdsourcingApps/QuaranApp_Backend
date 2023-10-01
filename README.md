# QuaranApp Backend

## MVP v.1

### DB Diagram

```mermaid
---
title: Quaranize Models
---
class Riwayah {
    <<enumeration>>
    Hafs
    Qaloon
}
class AyahPart {
    Uuid: id
    Uuid: ayahId
    Int: partNumber = 0
}
class Ayah {
    Uuid: id
    Riwayah: riwayah
    Int: surahNumber
    Int: ayahInSurahNumber
}
class User {
    String: id
    String: alias
    String: name
    String: surname
}
class Recording {
    Uuid: id
    String: userId
    AyahPart: start
    AyahPart: end 
    String: audioUrl
    Date: date
}
class SharedRecording {
    Uuid: recipientId
    Uuid: recordingId
    Date: date
}
Recording *-- AyahPart: consist of
User -- Recording: creates
AyahPart --> Ayah
Ayah --> Riwayah
SharedRecording --> Recording
```