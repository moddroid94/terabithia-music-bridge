# pylint: disable=invalid-name
# mypy: disable-error-code="import-untyped"
import logging
import base64

import music_tag
from mutagen.flac import FLAC

from models.models import TrackItemSlot

logger = logging.getLogger("Runner")


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


def get_flac_info(filePath):
    trackTags = {}
    track = FLAC(filePath)
    for i, v in track.tags.items():
        try:
            trackTags[i] = list(v)
        except:  # noqa: E722 #pylint: disable=W0702
            pass
    trackTags["LENGTH"] = track.info.length
    artbytes = track.pictures[0].data
    trackTags["ARTWORK"] = base64.b64encode(artbytes).decode()
    return trackTags
