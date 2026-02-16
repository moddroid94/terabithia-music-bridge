import logging
import liblistenbrainz

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
        listens = self.client.get_lb_radio(prompt, mode)
        return listens

    def get_candidates(self, playlist) -> list[CandidateTrack]:
        response = self._get_radio_json(playlist["prompt"], playlist["mode"])
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
