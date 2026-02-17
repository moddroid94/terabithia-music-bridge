from pydantic import BaseModel


class TrackItemSlot:
    def __init__(
        self,
        title,
        artist,
        album=None,
        id=None,
        duration=None,
        replayGain=None,
        trackNumber=None,
        volumeNumber=None,
        popularity=None,
        copyright=None,
        url=None,
        isrc=None,
        explicit=None,
        audioQuality=None,
        artists=None,
    ):
        self.id = id
        self.title = title
        self.duration = duration
        self.replayGain = replayGain
        self.trackNumber = trackNumber
        self.volumeNumber = volumeNumber
        self.popularity = popularity
        self.copyright = copyright
        self.url = url
        self.isrc = isrc
        self.explicit = explicit
        self.audioQuality = audioQuality
        self.artist: ArtistSubSlot = artist
        self.artists: dict[ArtistSubSlot] = artists
        self.album: AlbumSubSlot | AlbumItemSlot = album


class AlbumItemSlot:
    def __init__(
        self,
        id,
        title,
        duration,
        cover,
        date,
        numberOfTracks,
        numberOfVolumes,
        popularity,
        copyright,
        url,
        upc,
        explicit,
        audioQuality,
        artist,
        artists,
    ):
        self.id = id
        self.title = title
        self.duration = duration
        self.cover = cover
        self.date = date
        self.numberOfTracks = numberOfTracks
        self.numberOfVolumes = numberOfVolumes
        self.popularity = popularity
        self.copyright = copyright
        self.url = url
        self.upc = upc
        self.explicit = explicit
        self.audioQuality = audioQuality
        self.artist: ArtistSubSlot = artist
        self.artists: dict[ArtistSubSlot] = artists


class TrackInfoSlot:
    def __init__(
        self,
        trackId,
        trackReplayGain,
        albumReplayGain,
        bitDepth,
        sampleRate,
        manifest,
        url="",
        codec="",
    ):
        self.trackId = trackId
        self.trackReplayGain = trackReplayGain
        self.albumReplayGain = albumReplayGain
        self.bitDepth = bitDepth
        self.sampleRate = sampleRate
        self.manifest = manifest
        self.url = url
        self.codecs = codec


class ArtistSubSlot:
    def __init__(self, id, name, picture):
        self.id = id
        self.name = name
        self.picture = picture


class AlbumSubSlot:
    def __init__(self, id, title, cover):
        self.id = id
        self.title = title
        self.cover = cover


class CandidateTrack:
    def __init__(self, title, artist, album=None, id=None):
        self.title = title
        self.artist = artist
        self.album = album
        self.id = id


class BlueprintSlot(BaseModel):
    id: str
    name: str
    metaApi: str
    audioApi: str
    prompt: str
    enabled: bool
    every: str
    hour: str = "5"
    minute: str = "0"
    weekday: str = "*"
    day: str = "1"
    month: str = "*"
    description: str = ""
    mode: str = "easy"


class BlueprintSlotUpdate(BaseModel):
    id: str
    name: str | None = None
    metaApi: str | None = None
    audioApi: str | None = None
    prompt: str | None = None
    enabled: bool | None = None
    every: str | None = None
    hour: str | None = None
    minute: str | None = None
    weekday: str | None = None
    day: str | None = None
    month: str | None = None
    description: str | None = None
    mode: str | None = None
