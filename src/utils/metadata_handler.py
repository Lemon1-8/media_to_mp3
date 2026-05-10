import os
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TALB, TYER, APIC


class MetadataHandler:
    def read_metadata(self, path: str) -> dict | None:
        try:
            audio = MutagenFile(path)
            if audio is None:
                return None
            tags = {}
            for key in ("title", "artist", "album", "date", "year"):
                try:
                    tags[key] = str(audio.get(key, [""])[0]) if audio.get(key) else ""
                except Exception:
                    tags[key] = ""
            return tags
        except Exception:
            return None

    def write_tags(self, mp3_path: str, source_metadata: dict | None):
        if not source_metadata:
            return
        try:
            try:
                tags = ID3(mp3_path)
            except Exception:
                tags = ID3()

            if source_metadata.get("artist"):
                tags["TPE1"] = TPE1(encoding=3, text=source_metadata["artist"])
            if source_metadata.get("title"):
                tags["TIT2"] = TIT2(encoding=3, text=source_metadata["title"])
            if source_metadata.get("album"):
                tags["TALB"] = TALB(encoding=3, text=source_metadata["album"])
            year = source_metadata.get("year") or source_metadata.get("date", "")
            if year and year.isdigit():
                tags["TYER"] = TYER(encoding=3, text=year)

            tags.save(mp3_path)
        except Exception:
            pass
