import json
import base64


def json_from_base64(base64_bytes):
    return json.loads(base64.b64decode(base64_bytes).decode("utf-8"))


def match_candidate_to_track(candidateTrack, trackSlot) -> bool:
    # clean up titles to avoid punctuation differences between tidal and musicbrainz suggestions
    # it will miss some tracks if the title includes other infos
    trackTitle = "".join(x for x in trackSlot.title if (x.isalnum() or x in "._- "))
    compareTitle = "".join(
        x for x in candidateTrack.title if (x.isalnum() or x in "._- ")
    )

    # append only if name + artist is in the track infos
    if (
        (
            compareTitle.casefold() in trackTitle.casefold()
            or trackTitle.casefold() in compareTitle.casefold()
        )
        and (
            trackSlot.artist.name.casefold() in candidateTrack.artist.casefold()
            or candidateTrack.artist.casefold() in trackSlot.artist.name.casefold()
        )
    ) or (
        (
            compareTitle.casefold() in trackTitle.casefold()
            or trackTitle.casefold() in compareTitle.casefold()
        )
        and candidateTrack.artist.casefold()
        in [t.name.casefold() for t in trackSlot.artists]
    ):
        return True
    return False
