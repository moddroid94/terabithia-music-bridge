# pylint: disable=invalid-name
# mypy: disable-error-code="import-untyped"
import logging
import time

import liblistenbrainz
from fastapi import HTTPException

from models.models import CandidateTrack

logger = logging.getLogger("Runner")


class MetaLBZAPI:
    def __init__(self, token=None):
        self.token = token
        self.client = liblistenbrainz.ListenBrainz()
        if token is not None:
            self._set_auth()

    def _set_auth(self):
        self.client.set_auth_token(self.token)

    def _get_radio_json(self, prompt, mode="easy"):
        response = self.client.get_lb_radio(prompt, mode)
        return response

    def get_candidates(self, playlist) -> list[CandidateTrack]:
        retries = 3
        while retries > 0:
            response = self._get_radio_json(playlist["prompt"], playlist["mode"])
            match response.status_code:
                case 200:
                    break
                case 429:
                    retry_in = response.headers["X-RateLimit-Reset-In"]
                    retries = retries - 1
                    time.sleep(int(retry_in) + 5)
                case _:
                    retries = retries - 1
                    time.sleep(5)  # sleep some time

        if retries == 0:
            raise HTTPException(response.status_code)
        tracklist: list[CandidateTrack] = []

        for i in response["payload"]["jspf"]["playlist"]["track"]:
            candidateTrack = CandidateTrack(
                title=i["title"],
                artist=i["creator"],
                id=None,
            )
            logging.info(
                "Appending Item: Title: %s - Artist: %s",
                candidateTrack.title,
                candidateTrack.artist,
            )
            tracklist.append(candidateTrack)
        return tracklist
