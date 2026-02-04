import time
import base64
import json
from os import path, makedirs


from models import TrackItemSlot
import tagger
from linkapi import MetaLinkApi, AudioLinkApi
from utils import match_candidate_to_track


def main():
    with open("config.json", "rb") as conf:
        config = json.loads(conf.read())

    for playlist in config:
        fetch(playlist)


def fetch(playlist):
    print(f"Building playlist: {playlist['name']}")
    try:
        metaApi = MetaLinkApi(playlist["provider"], playlist["token"])
    except KeyError:
        metaApi = MetaLinkApi(playlist["provider"])
    audioApi = AudioLinkApi("hifi")

    trackList: list[TrackItemSlot] = []
    # get candidate tracks from api
    # API returns a list of CandidateTracks from a playlist config entry
    candidateList = metaApi.api.get_candidates(playlist)

    # matches candidates to available tracks
    # gets full metadata from api for every track and adds to queue

    for i in candidateList:
        # API returns a list of TrackItemSlot from a prompt
        trackSlotList = audioApi.api.search_track(f"{i.title} {i.artist}")

        for trackSlot in trackSlotList:
            # append only if name + artist is in the track infos
            print(
                f"Checking Item: Title: {i.title} Artist: {i.artist}\nWith: Title: {trackSlot.title} Artist: {trackSlot.artist.name} Feat: {[t.name for t in trackSlot.artists]}\n"
            )
            if match_candidate_to_track(i, trackSlot):
                # get additional album info if matching
                trackSlot.album = audioApi.api.get_album_info(trackSlot.album.id)
                trackList.append(trackSlot)
                print(f"Matched: {trackSlot.title} - {trackSlot.artist.name}\n")
                break  # breaks after the first match

        time.sleep(4)
        if len(trackList) > 10:
            break

    # get track files from queue list and
    # builds playlist appending tracks to the m3u
    m3u = []
    m3u.append("#EXTM3U")
    m3u.append(f"#{playlist['name']}")
    for t in trackList:
        # get file manifest and info
        trackInfoSlot = audioApi.api.get_track_manifest(t.id, t.audioQuality)

        # get artwork and audio file
        print(f"Downloading Item: Title: {t.title} - Artist: {t.artist.name}")
        time.sleep(1.5)
        trackBytes = audioApi.api.get_track_file(trackInfoSlot.url)
        trackArtworkBytes = audioApi.api.get_album_art(t.album.cover)

        albumTitle = "".join(x for x in t.album.title if (x.isalnum() or x in "._- "))
        # make dirs recursively
        try:
            dirPath = path.abspath(
                f"tracks/{playlist['name']}/{t.artist.name}/{albumTitle}"
            )
            makedirs(dirPath, exist_ok=True)
        except Exception as e:
            print(
                f"Error Making Directory: {dirPath} \nWith Error: {e.with_traceback()}"
            )

        # sanitize file name and builds filename
        fileTitle = "".join(x for x in t.title if (x.isalnum() or x in "._- "))

        filePath = path.abspath(
            f"tracks/{playlist['name']}/{t.artist.name}/{albumTitle}/{fileTitle} - {t.artist.name}.{trackInfoSlot.codecs}"
        )

        # write files to disk and append relative path to m3u
        time.sleep(4)
        try:
            with open(
                filePath,
                mode="wb",
            ) as file:
                file.write(trackBytes)
            m3u.append(
                f"{t.artist.name}/{albumTitle}/{fileTitle} - {t.artist.name}.{trackInfoSlot.codecs}"
            )
        except Exception as e:
            print(
                f"ERROR: Can't write: {fileTitle} - {t.artist.name}.{trackInfoSlot.codecs} \nError: {e.with_traceback()}"
            )

        # tag succesfully written files
        time.sleep(1)
        tagger.tag_flac(filePath, t)
        tagger.add_cover(filePath, trackArtworkBytes)
        print(f"Cover Added to Track: {t.title} - {t.artist.name}")

    # write m3u8 playlist file to disk
    with open(
        f"tracks/{playlist['name']}/{playlist['name']}.m3u8",
        encoding="utf-8",
        mode="w",
    ) as file:
        for line in m3u:
            file.write(line + "\n")
    print("Playlist downloaded")


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
