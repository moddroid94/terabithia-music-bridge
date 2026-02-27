from api.lbz_api import MetaLBZAPI
from api.hifi_api import AudioHifiAPI
from api.scl_api import YtSclAPI


class MetaLinkApi:
    def __init__(self, provider, token=None, path=""):
        self.provider = provider
        self.token = token
        self.path = path
        self.api = None
        self._set_provider()

    def _set_provider(self):
        match self.provider:
            case "lbz":
                self.api = MetaLBZAPI(self.token)
            case "scl":
                self.api = YtSclAPI(self.path)
            case _:
                raise NotImplementedError


class AudioLinkApi:
    def __init__(self, provider, token=None, path=""):
        self.provider = provider
        self.token = token
        self.path = path
        self.api = None
        self._set_provider()

    def _set_provider(self):
        match self.provider:
            case "hifi":
                self.api = AudioHifiAPI()
            case "scl":
                self.api = YtSclAPI(self.path)
            case _:
                raise NotImplementedError
