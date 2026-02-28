from urllib.parse import urljoin
import requests
import time
import json

import yt_dlp
from utils.utils import json_from_base64
from models.models import (
    TrackItemSlot,
    ArtistSubSlot,
    AlbumSubSlot,
    AlbumItemSlot,
    TrackInfoSlot,
)


def _artist_subslot(artistItem):
    return ArtistSubSlot(id="", name=artistItem, picture="")


def _album_subslot(albumItem):
    return AlbumSubSlot(id="", title=albumItem, cover="")


class YtSclAPI:
    def __init__(self, path=""):
        self.session = requests.Session()
        self.path = path
        self.opts = {
            "format": "bestaudio/best",
            "extractaudio": True,
            "audioformat": "mp3",
            "outtmpl": self.path + "/ass/moreass/songass.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
                {
                    "key": "EmbedThumbnail",
                },
            ],
            "writethumbnail": True,
            "logger": None,
            "overwrites": False,
        }
        self.ytDlp = yt_dlp.YoutubeDL(params=self.opts)

    def search_track(self, url) -> list[TrackItemSlot]:
        with self.ytDlp as file:
            response = file.extract_info(url=url, download=False)

        resultTracks = []
        for responseItem in response["entries"]:
            resultTracks.append(
                TrackItemSlot(
                    id=responseItem["id"],
                    title=responseItem["title"],
                    duration=responseItem["duration"],
                    url=responseItem["url"],
                    artist=_artist_subslot(responseItem.get("artist")),
                    artists=[_artist_subslot(i) for i in responseItem["artists"]],
                    album=_album_subslot(
                        responseItem["playlist"]
                        if responseItem["playlist"] is not None
                        else responseItem["genre"]
                    ),
                    thumbnail=responseItem["thumbnail"],
                    trackinfoslot=self.get_track_manifest(responseItem),
                )
            )
        return resultTracks

    def get_track_manifest(self, Track) -> TrackInfoSlot:
        trackInfoSlot = TrackInfoSlot(
            trackId=Track["id"],
            codec="mp3",  # hardcoded because is hardcoded in postprocessor so the final files will be mp3
            url=Track["url"],
        )

        return trackInfoSlot

    def get_track_file(self, Track: TrackInfoSlot) -> bytes:
        response = self.session.get(Track.url)
        return response.content

    def _get_album_subslot(self, item):
        try:
            item = item["album"]
        except KeyError:
            if item["playlist"] is not None:
                item = item["playlist"]
            else:
                item = item["genre"]
        return item

    def _get_tracklist_from_info(self, info) -> list[TrackItemSlot]:
        resultTracks = []
        # key "_type" seems not accessible? getting keyError.
        if info.get("entries"):
            for responseItem in info["entries"]:
                if responseItem["artists"] is not None:
                    artistlist = responseItem["artists"]
                else:
                    artistlist = ["unknown"]
                resultTracks.append(
                    TrackItemSlot(
                        id=responseItem["id"],
                        title=responseItem["title"],
                        duration=responseItem["duration"],
                        url=responseItem[
                            "original_url"
                        ],  # this is not the file url, but the page one, for yt-dlp
                        artist=_artist_subslot(responseItem.get("artist")),
                        artists=[_artist_subslot(i) for i in artistlist],
                        album=_album_subslot(self._get_album_subslot(responseItem)),
                        thumbnail=responseItem["thumbnail"],
                        trackinfoslot=self.get_track_manifest(responseItem),
                    )
                )
        else:
            responseItem = info
            if responseItem["artists"] is not None:
                artistlist = responseItem["artists"]
            else:
                artistlist = ["unknown"]
            resultTracks.append(
                TrackItemSlot(
                    id=responseItem["id"],
                    title=responseItem["title"],
                    duration=responseItem["duration"],
                    url=responseItem["url"],
                    artist=_artist_subslot(responseItem.get("artist")),
                    artists=[_artist_subslot(i) for i in responseItem["artists"]],
                    album=_album_subslot(self._get_album_subslot(responseItem)),
                    thumbnail=responseItem["thumbnail"],
                    trackinfoslot=self.get_track_manifest(responseItem),
                )
            )
        return resultTracks

    def let_download_url(self, url, logger, outputPath, idx):
        opts = self.opts
        opts["logger"] = logger
        opts["outtmpl"] = self.path + outputPath + ".%(ext)s"
        opts["playlist_items"] = str(idx)
        with yt_dlp.YoutubeDL(params=opts) as ydl:
            info = ydl.extract_info(url, download=True)
            logger.debug("DOWNLOAD INFO: %s", json.dumps(ydl.sanitize_info(info)))

    def get_info_url(self, url, logger) -> list[TrackItemSlot]:
        opts = self.opts
        opts["logger"] = logger
        with yt_dlp.YoutubeDL(params=opts) as ydl:
            info = ydl.extract_info(url, download=False, process=True)
            logger.debug("INFO: %s", json.dumps(ydl.sanitize_info(info)))
            tracklist = self._get_tracklist_from_info(info)
        return tracklist

    def get_album_art(self, Track: TrackItemSlot) -> bytes:
        """
        Get valid urls to album art and return artwork bytes.

        :param uuid: Album art uuid (can be found as cover property in album object)
        :type uuid: string

        :return: Artwork bytes object.
        :rtype: bytes
        """
        response = self.session.get(Track.thumbnail)
        return response.content
