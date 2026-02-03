from urllib.parse import urljoin

import requests


class SquidAPI:
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

        return response

    def search_track(self, prompt, mode="s"):
        params = {
            mode: prompt,
        }
        response = self._make_request(self.search_path, params)
        return response.json()

    def get_track_info(self, track_id, quality="LOSSLESS"):
        params = {"id": track_id, "quality": quality}

        response = self._make_request(self.track_path, params)
        return response.json()

    def get_album_info(self, album_id):
        params = {"id": album_id}

        response = self._make_request(self.album_path, params)
        return response.json()

    def get_track_file(self, url):
        response = self.session.get(url)
        return response.content

    def get_album_art_from_uuid(self, uuid):
        """
        Get valid urls to album art.

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
