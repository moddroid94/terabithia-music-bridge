from lbz_api import ListenBrainzAPI
from hifi_api import AudioHifiAPI


class MetaLinkApi:
    def __init__(self, provider, token=None):
        self.provider = provider
        self.token = token
        self.api = None
        self._set_provider()

    def _set_provider(self):
        match self.provider:
            case "lbz":
                self.api = ListenBrainzAPI(self.token)
            case "hifi":
                raise NotImplementedError
            case _:
                raise NotImplementedError


class AudioLinkApi:
    def __init__(self, provider, token=None):
        self.provider = provider
        self.token = token
        self.api = None
        self._set_provider()

    def _set_provider(self):
        match self.provider:
            case "hifi":
                self.api = AudioHifiAPI()
            case _:
                raise NotImplementedError
