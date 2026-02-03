import liblistenbrainz


class ListenBrainzAPI:
    def __init__(self, username, token=""):
        self.token = token
        self.username = username
        self.client = liblistenbrainz.ListenBrainz()
        if token != "":
            self._set_auth()

    def _set_auth(self):
        self.client.set_auth_token(self.token)

    def get_radio_json(self, prompt, mode="easy"):
        listens = self.client.get_lb_radio(prompt, mode)
        return listens
