import time
import json
from os import path, makedirs, walk
import logging

from models.models import TrackItemSlot
from core import tagger
from api.linkapi import MetaLinkApi, AudioLinkApi
from utils.utils import match_candidate_to_track


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=f"logs/run{time.time()}.log", encoding="utf-8", level=logging.DEBUG
)

logger.info("Logging Initialized")


def main():
    with open("config.json", "rb") as conf:
        config = json.loads(conf.read())
    logger.info("Configuration loaded")

    blueprints = []
    for dirpath, dirnames, filenames in walk(path.abspath("blueprints")):
        logger.info("Scanning %s", dirpath)
        for file in filenames:
            blueprints.append(path.join(dirpath, file))
            logger.info("Found Blueprint %s", file)
        break

    for playlist in blueprints:
        with open(playlist, "rb") as item:
            playlistEntry = json.loads(item.read())
        fetch(playlistEntry, config)


def fetch(playlist, config):
    logger.info("Building playlist: %s", playlist["name"])
    try:
        metaApi = MetaLinkApi(playlist["metaApi"], config["token"])
    except KeyError:
        metaApi = MetaLinkApi(playlist["metaApi"])
    audioApi = AudioLinkApi(playlist["audioApi"])

    trackList: list[TrackItemSlot] = []
    # get candidate tracks from api
    # API returns a list of CandidateTracks from a playlist config entry
    candidateList = metaApi.api.get_candidates(playlist)

    # matches candidates to available tracks
    # gets full metadata from api for every track and adds to queue

    for i in candidateList:
        # API returns a list of TrackItemSlot from a prompt
        trackSlotList = audioApi.api.search_track(f"{i.title} {i.artist}")

        for trackSlot in trackSlotList:
            # append only if name + artist is in the track infos
            logger.info(
                "Checking Item: Title: %s Artist: %s\nWith: Title: %s Artist: %s Feat: %s\n",
                i.title,
                i.artist,
                trackSlot.title,
                trackSlot.artist.name,
                [t.name for t in trackSlot.artists],
            )
            if match_candidate_to_track(i, trackSlot):
                # get additional album info if matching
                trackSlot.album = audioApi.api.get_album_info(trackSlot.album.id)
                trackList.append(trackSlot)
                logger.info(
                    "Matched: %s - %s\n", trackSlot.title, trackSlot.artist.name
                )
                break  # breaks after the first match

        time.sleep(4)
        if len(trackList) > 10:
            break

    # get track files from queue list and
    # builds playlist appending tracks to the m3u
    m3u = []
    m3u.append("#EXTM3U")
    m3u.append(f"#{playlist['name']}")
    for t in trackList:
        # get file manifest and info
        trackInfoSlot = audioApi.api.get_track_manifest(t.id, t.audioQuality)

        # get artwork and audio file
        logger.info("Downloading Item: Title: %s - Artist: %s", t.title, t.artist.name)
        time.sleep(1.5)
        trackBytes = audioApi.api.get_track_file(trackInfoSlot.url)
        trackArtworkBytes = audioApi.api.get_album_art(t.album.cover)

        albumTitle = "".join(x for x in t.album.title if (x.isalnum() or x in "._- "))
        # make dirs recursively
        try:
            dirPath = path.abspath(
                f"tracks/{playlist['name']}/{t.artist.name}/{albumTitle}"
            )
            makedirs(dirPath, exist_ok=True)
        except OSError as e:
            logger.error(
                "Error Making Directory: %s \nWith Error: %s",
                dirPath,
                e,
                exc_info=True,
            )

        # sanitize file name and builds filename
        fileTitle = "".join(x for x in t.title if (x.isalnum() or x in "._- "))

        filePath = path.abspath(
            f"tracks/{playlist['name']}/{t.artist.name}/{albumTitle}/{fileTitle} - {t.artist.name}.{trackInfoSlot.codecs}"
        )

        # write files to disk and append relative path to m3u
        time.sleep(4)
        try:
            with open(
                filePath,
                mode="wb",
            ) as file:
                file.write(trackBytes)
            m3u.append(
                f"{t.artist.name}/{albumTitle}/{fileTitle} - {t.artist.name}.{trackInfoSlot.codecs}"
            )
        except OSError as e:
            logger.error(
                "ERROR: Can't write: %s - %s.%s \nError: %s",
                fileTitle,
                t.artist.name,
                trackInfoSlot.codecs,
                e,
                exc_info=True,
            )

        # tag succesfully written files
        time.sleep(1)
        tagger.tag_flac(filePath, t)
        tagger.add_cover(filePath, trackArtworkBytes)
        logger.info("Cover Added to Track: %s - %s", t.title, t.artist.name)

    # write m3u8 playlist file to disk
    with open(
        f"tracks/{playlist['name']}/{playlist['name']}.m3u8",
        encoding="utf-8",
        mode="w",
    ) as file:
        for line in m3u:
            file.write(line + "\n")
    logger.info("Playlist %s downloaded", playlist["name"])


if __name__ == "__main__":
    main()
