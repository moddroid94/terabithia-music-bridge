from urllib.parse import urljoin
import requests

from utils.utils import json_from_base64
from models.models import (
    TrackItemSlot,
    ArtistSubSlot,
    AlbumSubSlot,
    AlbumItemSlot,
    TrackInfoSlot,
)


def _artist_subslot(artistItem):
    return ArtistSubSlot(
        id=artistItem["id"], name=artistItem["name"], picture=artistItem["picture"]
    )


def _album_subslot(albumItem):
    return AlbumSubSlot(
        id=albumItem["id"], title=albumItem["title"], cover=albumItem["cover"]
    )


class AudioHifiAPI:
    def __init__(self):
        self.api_urls = [
            "https://triton.squid.wtf",
            "https://vogel.qqdl.site",
            "https://tidal.kinoplus.online",
            "https://tidal-api.binimum.org",
        ]
        self.search_path = "/search/"
        self.track_path = "/track/"
        self.album_path = "/album/"
        self.info_path = "/info/"
        self.recommendations_path = "/recommendations/"

        self.session = None
        self.session = requests.Session()

    def _make_request(self, path_url, params):
        for u in self.api_urls:
            response = self.session.get(urljoin(u, path_url), params=params)
            if response.ok:
                break
        if response.ok:
            return response.json()
        raise ConnectionError

    def search_track(self, prompt, mode="s") -> list[TrackItemSlot]:
        params = {
            mode: prompt,
        }
        response = self._make_request(self.search_path, params)

        resultTracks = []
        for responseItem in response["data"]["items"]:
            resultTracks.append(
                TrackItemSlot(
                    id=responseItem["id"],
                    title=responseItem["title"],
                    duration=responseItem["duration"],
                    replayGain=responseItem["replayGain"],
                    trackNumber=responseItem["trackNumber"],
                    volumeNumber=responseItem["volumeNumber"],
                    popularity=responseItem["popularity"],
                    copyright=responseItem["copyright"],
                    url=responseItem["url"],
                    isrc=responseItem["isrc"],
                    explicit=responseItem["explicit"],
                    audioQuality=responseItem["audioQuality"],
                    artist=_artist_subslot(responseItem["artist"]),
                    artists=[_artist_subslot(i) for i in responseItem["artists"]],
                    album=_album_subslot(responseItem["album"]),
                )
            )
        return resultTracks

    def get_track_manifest(self, track_id, quality="LOSSLESS") -> TrackInfoSlot:
        params = {"id": track_id, "quality": quality}

        response = self._make_request(self.track_path, params)
        decodedManifest = json_from_base64(response["data"]["manifest"])

        trackInfoSlot = TrackInfoSlot(
            trackId=response["data"]["trackId"],
            trackReplayGain=response["data"]["trackReplayGain"],
            albumReplayGain=response["data"]["albumReplayGain"],
            bitDepth=response["data"]["bitDepth"],
            sampleRate=response["data"]["sampleRate"],
            manifest=response["data"]["manifest"],
            codec=decodedManifest["codecs"],
            url=decodedManifest["urls"][0],
        )

        if trackInfoSlot.url != "":
            return trackInfoSlot
        raise FileNotFoundError

    def get_album_info(self, album_id) -> AlbumItemSlot:
        params = {"id": album_id}

        response = self._make_request(self.album_path, params)
        responseData = response["data"]
        return AlbumItemSlot(
            id=responseData["id"],
            title=responseData["title"],
            duration=responseData["duration"],
            cover=responseData["cover"],
            date=responseData["releaseDate"],
            numberOfTracks=responseData["numberOfTracks"],
            numberOfVolumes=responseData["numberOfVolumes"],
            popularity=responseData["popularity"],
            copyright=responseData["copyright"],
            url=responseData["url"],
            upc=responseData["upc"],
            explicit=responseData["explicit"],
            audioQuality=responseData["audioQuality"],
            artist=_artist_subslot(responseData["artist"]),
            artists=[_artist_subslot(i) for i in responseData["artists"]],
        )

    def get_track_file(self, url) -> bytes:
        response = self.session.get(url)
        return response.content

    def get_album_art(self, uuid) -> bytes:
        """
        Get valid urls to album art and return artwork bytes.

        :param uuid: Album art uuid (can be found as cover property in album object)
        :type uuid: string

        :return: Artwork bytes object.
        :rtype: bytes
        """

        baseUrl = f"https://resources.tidal.com/images/{uuid.replace('-', '/')}"

        images = {
            "sm": f"{baseUrl}/160x160.jpg",
            "md": f"{baseUrl}/320x320.jpg",
            "lg": f"{baseUrl}/640x640.jpg",
            "xl": f"{baseUrl}/1080x1080.jpg",
            "xxl": f"{baseUrl}/1280x1280.jpg",
        }
        response = self.session.get(images["lg"])
        return response.content
