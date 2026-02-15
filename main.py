import time
import json
from os import path, makedirs, walk
import logging
import threading

from fastapi import HTTPException, FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
import schedule

from core import tagger
from models.models import BlueprintSlot, BlueprintSlotUpdate, TrackItemSlot
from api.linkapi import MetaLinkApi, AudioLinkApi
from utils.utils import match_candidate_to_track


app = FastAPI()

# Initialize
with open("config.json", "rb") as conf:
    config = json.loads(conf.read())
logger = logging.getLogger(__name__)
logger.info("Configuration loaded")
logging.basicConfig(
    filename=f"logs/main_{time.time()}.log",
    encoding="utf-8",
    level=config["logLevel"],
)
logger.info("Logging Initialized")

cease_continuous_run = threading.Event()
threads = []


# Blueprints Methods
@app.get("/blueprints/all", response_model=list[BlueprintSlot])
def get_blueprints() -> list[BlueprintSlot]:
    """
    returns a list of blueprints, fails if any of the blueprints is malformed
    """
    blueprints = []
    for dirpath, dirnames, filenames in walk(
        path.abspath("blueprints"),
        onerror=(logger.error("Error in Scan Blueprint Directory")),
    ):
        logger.info("Scanning %s", dirpath)
        for file in filenames:
            blueprints.append(path.join(dirpath, file))
            logger.info("Found Blueprint %s", file)
        break  # return only root bp folder

    blueprintSlots: list[BlueprintSlot] = []
    for playlist in blueprints:
        with open(playlist, "rb") as item:
            playlistEntry = json.loads(item.read())
            try:
                blueprintSlots.append(BlueprintSlot(**playlistEntry))
            except ValidationError as e:
                logger.error("Key Not Found %s", e, exc_info=True)
                raise HTTPException(
                    444, "Blueprint Validaiton error, check Logs"
                ) from e

    return blueprintSlots


@app.patch("/blueprint/{name}")
def set_blueprint(name: str, item: BlueprintSlotUpdate) -> BlueprintSlot:
    """
    Edits as blueprint given the name and a json with updated fields
    return: 445 | 446 | BlueprintSlot
    """
    blueprints = []
    for dirpath, dirnames, filenames in walk(
        path.abspath("blueprints"),
        onerror=(logger.error("Error in Scan Blueprint Directory")),
    ):
        logger.info("Scanning %s", dirpath)
        for file in filenames:
            blueprints.append(path.join(dirpath, file))
            logger.info("Found Blueprint %s", file)
        break  # return only root bp folder

    updated_item = None
    for playlist in blueprints:
        with open(playlist, "rb") as p:
            playlistEntry = json.loads(p.read())
            if playlistEntry["name"] != name:
                continue

        try:
            stored_item_model = BlueprintSlot(**playlistEntry)
            update_data = item.model_dump(exclude_unset=True)
            updated_item = stored_item_model.model_copy(update=update_data)
        except Exception as e:
            logger.error(
                "Error editing blueprint %s \nError: %s",
                playlistEntry["name"],
                e,
                exc_info=True,
            )
            raise HTTPException(445, "Error editing blueprint, check Logs") from e

        try:
            with open(playlist, "w", encoding="utf-8") as p:
                json.dump(jsonable_encoder(updated_item), p, ensure_ascii=False)
                break
        except Exception as e:
            logger.error("Error on writing blueprint %s", e, exc_info=True)
            raise HTTPException(446, "Error on writing blueprint, check logs") from e

    return updated_item


# Scheduler Endpoints
@app.post("/scheduler/set/{playlistName}")
def set_job(playlistName: str, every: list[str], at: str):
    jobs = schedule.get_jobs(playlistName)
    if len(jobs) > 0:
        schedule.clear(playlistName)
    if "monday" in every:
        schedule.every().monday.at(at).do(fetch, playlistName).tag(playlistName)
    if "tuesday" in every:
        schedule.every().tuesday.at(at).do(fetch, playlistName).tag(playlistName)
    if "wednesday" in every:
        schedule.every().wednesday.at(at).do(fetch, playlistName).tag(playlistName)
    if "thursday" in every:
        schedule.every().thursday.at(at).do(fetch, playlistName).tag(playlistName)
    if "friday" in every:
        schedule.every().friday.at(at).do(fetch, playlistName).tag(playlistName)
    if "saturday" in every:
        schedule.every().saturday.at(at).do(fetch, playlistName).tag(playlistName)
    if "sunday" in every:
        schedule.every().sunday.at(at).do(fetch, playlistName).tag(playlistName)


@app.post("/schedule/clear/{playlistName}")
def clean_job(playlistName):
    schedule.clear(playlistName)


@app.get("/scheduler/all")
def get_jobs():
    jobs = schedule.get_jobs()
    return {
        json.dumps([str(job), str(job.at_time), str(job.start_day)]) for job in jobs
    }


@app.post("/scheduler/{enabled}")
def toggle_scheduler(enabled: bool):
    if len(threads) > 0:
        if threads[0].is_alive():
            if not enabled:
                cease_continuous_run.set()
                threads[0].join()
                threads.clear()
                return "killed and cleaned"
            return "already running"
        if not threads[0].is_alive():
            if enabled:
                threads[0].join()
                threads.clear()
                cease_continuous_run.clear()
                spawn_thread()
                return "relaunched zombie"
            threads[0].join()
            threads.clear()
            return "cleaned zolmbie threads"
    if enabled:
        cease_continuous_run.clear()
        spawn_thread()
        return "build and run thread"
    return "No threads running"


def spawn_thread(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    threads.append(continuous_thread)


def fetch(playlistName):
    blueprints = []
    playlist = None
    for dirpath, dirnames, filenames in walk(
        path.abspath("blueprints"),
        onerror=logger.error("Error in Scan Blueprint Directory"),
    ):
        logger.info("Scanning %s", dirpath)
        for file in filenames:
            blueprints.append(path.join(dirpath, file))
            logger.info("Found Blueprint %s", file)
        break  # return only root bp folder

    for p in blueprints:
        with open(p, "rb") as item:
            playlistEntry = json.loads(item.read())
            if playlistEntry["name"] == playlistName:
                playlist = playlistEntry
                break
    if playlist is None:
        logger.error("No Playlist Found for %s", playlistName)
        return HTTPException(447, "No Playlist Found")
    logger.info("Building playlist: %s", playlist["name"])
    try:
        metaApi = MetaLinkApi(playlist["metaApi"], config["token"])
    except KeyError:
        metaApi = MetaLinkApi(playlist["metaApi"])
    audioApi = AudioLinkApi(playlist["audioApi"])

    trackList: list[TrackItemSlot] = []
    # get candidate tracks from api
    # API returns a list of CandidateTracks from a playlist config entry
    candidateList = metaApi.api.get_candidates(playlist)
    logger.info("got candidates")
    return
    # matches candidates to available tracks
    # gets full metadata from api for every track and adds to queue

    for i in candidateList:
        # API returns a list of TrackItemSlot from a prompt
        trackSlotList = audioApi.api.search_track(f"{i.title} {i.artist}")

        for trackSlot in trackSlotList:
            # append only if name + artist is in the track infos
            logger.info(
                "Checking Item: Title: %s Artist: %s\nWith: Title: %s Artist: %s Feat: %s\n",
                i.title,
                i.artist,
                trackSlot.title,
                trackSlot.artist.name,
                [t.name for t in trackSlot.artists],
            )
            if match_candidate_to_track(i, trackSlot):
                # get additional album info if matching
                trackSlot.album = audioApi.api.get_album_info(trackSlot.album.id)
                trackList.append(trackSlot)
                logger.info(
                    "Matched: %s - %s\n", trackSlot.title, trackSlot.artist.name
                )
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
        logger.info("Downloading Item: Title: %s - Artist: %s", t.title, t.artist.name)
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
        except OSError as e:
            logger.error(
                "Error Making Directory: %s \nWith Error: %s",
                dirPath,
                e,
                exc_info=True,
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
        except OSError as e:
            logger.error(
                "ERROR: Can't write: %s - %s.%s \nError: %s",
                fileTitle,
                t.artist.name,
                trackInfoSlot.codecs,
                e,
                exc_info=True,
            )

        # tag succesfully written files
        time.sleep(1)
        tagger.tag_flac(filePath, t)
        tagger.add_cover(filePath, trackArtworkBytes)
        logger.info("Cover Added to Track: %s - %s", t.title, t.artist.name)

    # write m3u8 playlist file to disk
    with open(
        f"tracks/{playlist['name']}/{playlist['name']}.m3u8",
        encoding="utf-8",
        mode="w",
    ) as file:
        for line in m3u:
            file.write(line + "\n")
    logger.info("Playlist %s downloaded", playlist["name"])
