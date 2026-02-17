from models.models import (
    TrackItemSlot,
    ArtistSubSlot,
    AlbumSubSlot,
    TrackInfoSlot,
    AlbumItemSlot,
    CandidateTrack,
)


def _artist_subslot(artistItem):
    return ArtistSubSlot(
        id=artistItem["id"], name=artistItem["name"], picture=artistItem["picture"]
    )


def _album_subslot(albumItem):
    return AlbumSubSlot(
        id=albumItem["id"], title=albumItem["title"], cover=albumItem["cover"]
    )


def TrackSlotFromResponseItem(responseItem) -> TrackItemSlot:
    return TrackItemSlot(
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


def AlbumSlotFromResponseData(responseData) -> AlbumItemSlot:
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


def TrackInfoSlotFromResponseData(responseData) -> TrackInfoSlot:
    return TrackInfoSlot(
        trackId=responseData["trackId"],
        trackReplayGain=responseData["trackReplayGain"],
        albumReplayGain=responseData["albumReplayGain"],
        bitDepth=responseData["bitDepth"],
        sampleRate=responseData["sampleRate"],
        manifest=responseData["manifest"],
    )


def CandidateTrackFromMetadataAPI(metadataResponse, ApiProvider):
    match ApiProvider:
        case "hifi":
            pass
        case "lbz":
            pass
        case _:
            raise NotImplementedError

    return CandidateTrack(
        metadataResponse["title"],
        metadataResponse["creator"],
        metadataResponse["album"],
        metadataResponse["id"],
    )
