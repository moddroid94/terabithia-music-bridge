class TrackItemSlot:
    def __init__(
        self,
        id,
        title,
        duration,
        replayGain,
        trackNumber,
        volumeNumber,
        popularity,
        copyright,
        url,
        isrc,
        explicit,
        audioQuality,
        artist,
        artists,
        album,
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
        self, trackId, trackReplayGain, albumReplayGain, bitDepth, sampleRate, manifest
    ):
        self.trackId = trackId
        self.trackReplayGain = trackReplayGain
        self.albumReplayGain = albumReplayGain
        self.bitDepth = bitDepth
        self.sampleRate = sampleRate
        self.manifest = manifest


class TrackManifest:
    def __init__(self, codec, url):
        self.codecs = codec
        self.url = url


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


class TrackItem:
    def __init__(self, album, creator, title):
        self.album = album
        self.creator = creator
        self.title = title
