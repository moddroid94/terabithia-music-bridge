import logging

import music_tag
from mutagen.flac import FLAC

from models.models import TrackItemSlot

logger = logging.getLogger(__name__)


def tag_flac(filePath, trackItemSlot: TrackItemSlot):
    trackTags = {
        "TITLE": [trackItemSlot.title],
        "ALBUM": [trackItemSlot.album.title],
        "ALBUMARTIST": [trackItemSlot.album.artist.name],
        "DATE": [trackItemSlot.album.date],
        "GENRE": [""],  # needs a source!
        "ARTIST": [trackItemSlot.artist.name],
        "ARTISTS": [a.name for a in trackItemSlot.artists],
        "TRACKNUMBER": [str(trackItemSlot.trackNumber)],
        "DISCNUMBER": [str(trackItemSlot.volumeNumber)],
        "TRACKTOTAL": [str(trackItemSlot.album.numberOfTracks)],
        "DISCTOTAL": [str(trackItemSlot.album.numberOfVolumes)],
        "ISRC": [trackItemSlot.isrc],
        "BARCODE": [trackItemSlot.album.upc],
        "REPLAYGAIN_TRACK_GAIN": [str(trackItemSlot.replayGain)],
        "COPYRIGHT": [trackItemSlot.copyright],
    }
    track = FLAC(filePath)
    for idx, tag in trackTags.items():
        track[idx] = tag
        logging.info(
            "Wrote Tag: %s With Value: %s \nFor Track File: %s", idx, tag, filePath
        )
    track.save()


def add_cover(FilePath, artworkBytes):
    track = music_tag.load_file(FilePath)

    # Add a new picture
    track["artwork"] = artworkBytes
    track.save()
