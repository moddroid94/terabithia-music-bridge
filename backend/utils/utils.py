import json
import base64
from os import path, walk

from core.tagger import get_flac_info, get_mp3_info


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


def generate_report(playlistName, runnedAt, blueprint, logger, error_callback):
    playlists = []
    filelist = []
    tracklist = []

    # pylint: disable-next=unused-variable
    for dirpath, dirnames, filenames in walk(
        path.abspath("output/playlists"),
        onerror=error_callback,
    ):
        logger.debug("Scanning %s", dirpath)
        for file in filenames:
            playlists.append(path.join(dirpath, file))
            logger.debug("Found Playlist %s", file)
        break  # return only root bp folder

    for p in playlists:
        logger.info("reading %s", p)
        with open(p, "r", encoding="utf-8") as item:
            lines = item.readlines()
            logger.info("reading %s", lines[1])
            if playlistName in lines[1]:
                for t in lines[2:]:
                    filelist.append(
                        t[3:-1]
                    )  # slice to remove the ../ and \n from the track line

    for f in filelist:
        logger.info("reading %s", f)
        rel_path = f"output/{f}"
        ext = f.split(".")[-1]
        full_path = path.abspath(rel_path)
        data = None
        if ext == "flac":
            data = get_flac_info(full_path)
        if ext == "mp3":
            data = get_mp3_info(full_path)

        tracklist.append(data)

    if len(tracklist) < 1:
        logger.error("No Playlist Found for %s", playlistName)
        return None
    report = {
        "name": playlistName,
        "runnedAt": runnedAt,
        "blueprint": blueprint,
        "tracklist": tracklist,
    }
    return report


def get_blueprint_match(playlistName, logger, error_callback):
    blueprints = []
    playlist = None
    # pylint: disable-next=unused-variable
    for dirpath, dirnames, filenames in walk(
        path.abspath("blueprints"),
        onerror=error_callback,
    ):
        logger.debug("Scanning %s", dirpath)
        for file in filenames:
            blueprints.append(path.join(dirpath, file))
            logger.debug("Found Blueprint %s", file)
        break  # return only root bp folder

    for p in blueprints:
        with open(p, "rb") as item:
            playlistEntry = json.loads(item.read())
            if playlistEntry["name"] == playlistName:
                playlist = playlistEntry
                break
    if playlist is None:
        logger.error("No Playlist Found for %s", playlistName)
        return None
    return playlist
