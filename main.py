import time
import base64
import json
from os import path, makedirs

from lb_handler import ListenBrainzAPI
from squid_api import SquidAPI
from constructor import (
    TrackSlotFromResponseItem,
    AlbumSlotFromResponseData,
    TrackInfoSlotFromResponseData,
    TrackManifestFromInfoManifest,
    TrackItemFromJSPFTrack,
)
from models import TrackItem, TrackItemSlot
import tagger


def main():
    auth_token = ""

    api = ListenBrainzAPI("x4b1d", auth_token)
    sqd = SquidAPI()

    # get playlist from listenbrainz
    response = api.get_radio_json("recs:x4b1d::unlistened")

    # get basic info for every track in the playlist
    tracklist: list[TrackItem] = []
    for i in response["payload"]["jspf"]["playlist"]["track"]:
        trackItem = TrackItemFromJSPFTrack(i)
        print(f"Appending Item: Title: {trackItem.title} - Artist: {trackItem.creator}")
        tracklist.append(trackItem)

    # get full metadata from api for every track and adds to queue if matching
    queue_list: list[TrackItemSlot] = []
    for i in tracklist:
        response = sqd.search_track(f"{i.title} {i.creator}")

        trackSlot = TrackSlotFromResponseItem(response["data"]["items"][0])
        print(
            f"Checking Item: Title: {i.title} Artist: {i.creator}\nWith: Title: {trackSlot.title} Artist: {trackSlot.artist.name} Feat: {[t.name for t in trackSlot.artists]}\n"
        )
        # append only if name + artist is in the track infos
        # clean up titles to avoid punctuation differences between tidal and musicbrainz suggestions
        trackTitle = "".join(x for x in i.title if (x.isalnum() or x in "._- "))
        compareTitle = "".join(
            x for x in trackSlot.title if (x.isalnum() or x in "._- ")
        )
        if (
            (
                compareTitle.casefold() in trackTitle.casefold()
                or trackTitle.casefold() in compareTitle.casefold()
            )
            and (
                trackSlot.artist.name.casefold() in i.creator.casefold()
                or i.creator.casefold() in trackSlot.artist.name.casefold()
            )
        ) or (
            (
                compareTitle.casefold() in trackTitle.casefold()
                or trackTitle.casefold() in compareTitle.casefold()
            )
            and i.creator.casefold() in [t.name.casefold() for t in trackSlot.artists]
        ):
            print(
                f"FOUND Item: Title: {trackSlot.title} Artist: {trackSlot.artist.name} Feat: {[t.name for t in trackSlot.artists]}\n"
            )
            albumResponse = sqd.get_album_info(trackSlot.album.id)
            trackSlot.album = AlbumSlotFromResponseData(albumResponse["data"])
            queue_list.append(trackSlot)
        time.sleep(4)
        if len(queue_list) > 1:
            break

    # get track files from queue list and
    # builds playlist appending tracks to the m3u
    m3u = []
    m3u.append("#EXTM3U")
    m3u.append("#PLAYLISTX")
    for t in queue_list:
        response = sqd.get_track_info(t.id, t.audioQuality)

        # get track mpd and manifest
        trackInfoSlot = TrackInfoSlotFromResponseData(response["data"])
        trackManifest = TrackManifestFromInfoManifest(trackInfoSlot.manifest)

        print(f"Downloading Item: Title: {t.title} - Artist: {t.artist.name}")

        # get artwork and audio file
        time.sleep(1.5)
        trackBytes = sqd.get_track_file(trackManifest.url)
        trackArtworkBytes = sqd.get_album_art_from_uuid(t.album.cover)

        # make dirs recursively
        try:
            dirPath = path.abspath(f"tracks/playlistx/{t.artist.name}/{t.album.title}")
            makedirs(dirPath, exist_ok=True)
        except Exception as e:
            print(
                f"Error Making Directory: {dirPath} \nWith Error: {e.with_traceback()}"
            )

        # sanitize file name and builds filename
        fileTitle = "".join(x for x in t.title if (x.isalnum() or x in "._- "))
        filePath = path.abspath(
            f"tracks/playlistx/{t.artist.name}/{t.album.title}/{fileTitle} - {t.artist.name}.{trackManifest.codecs}"
        )

        # write files to disk and append to m3u
        time.sleep(4)
        try:
            with open(
                filePath,
                mode="wb",
            ) as file:
                file.write(trackBytes)
            m3u.append(
                f"{t.artist.name}/{t.album.title}/{fileTitle} - {t.artist.name}.{trackManifest.codecs}"
            )
        except Exception as e:
            print(
                f"ERROR: Can't write: {fileTitle} - {t.artist.name}.{trackManifest.codecs} \nError: {e.with_traceback()}"
            )

        # tag succesfully written files
        time.sleep(1)
        tagger.tag_flac(filePath, t)
        tagger.add_cover(filePath, trackArtworkBytes)

    # write m3u8 playlist file to disk
    with open(
        "tracks/playlistx/playlistx.m3u8",
        encoding="utf-8",
        mode="w",
    ) as file:
        for line in m3u:
            file.write(line + "\n")


def get_search_result():
    auth_token = ""

    api = ListenBrainzAPI("x4b1d", auth_token)
    sqd = SquidAPI()

    result = sqd.search_track("crank")
    time.sleep(0.5)
    track = sqd.get_track_info(
        result["data"]["items"][0]["id"], result["data"]["items"][0]["audioQuality"]
    )
    track_manifest = json.loads(
        base64.b64decode(track["data"]["manifest"]).decode("utf-8")
    )
    track_b = sqd.get_track_file(track_manifest["urls"][0])
    with open(
        f"{result['data']['items'][0]['title']}.{track_manifest['codecs']}", mode="wb"
    ) as file:
        file.write(track_b)


if __name__ == "__main__":
    main()
