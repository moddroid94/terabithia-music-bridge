import time
import json
from os import path, makedirs, walk
import logging
from contextlib import asynccontextmanager

from fastapi import HTTPException, FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.jobstores.memory import MemoryJobStore

from core import tagger
from models.models import BlueprintSlot, BlueprintSlotUpdate, TrackItemSlot
from api.linkapi import MetaLinkApi, AudioLinkApi
from utils.utils import match_candidate_to_track

# Initialize logging
with open("config.json", "rb") as conf:
    config = json.loads(conf.read())
logger = logging.getLogger(__name__)
logger.info("Configuration loaded")
logging.basicConfig(
    filename="logs/main.log",
    encoding="utf-8",
    level=config["logLevel"],
)
logger.info("App Starting")


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

    metaApi = MetaLinkApi(playlist["metaApi"], config["token"])
    audioApi = AudioLinkApi(playlist["audioApi"])

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


# Initialize scheduler
jbs_name = "jbs_name"
schedule_store_path = path.abspath("data/schedule.json")
job_defaults_config = {"coalesce": True}
jobstore_config = {jbs_name: MemoryJobStore()}
scheduler = BackgroundScheduler(
    job_defaults=job_defaults_config,
    jobstores=jobstore_config,
    logger=logging.getLogger("APScheduler"),
)
try:
    scheduler.import_jobs(schedule_store_path, jbs_name)
except Exception as e:
    logger.error("No schedules found, starting fresh. error: %s", e, exc_info=True)
scheduler.start()


# Initialize FastAPI
# Ensure the scheduler shuts down properly on application exit.
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.export_jobs(schedule_store_path)
    scheduler.shutdown()
    logger.info("Scheduler shutdown")


app = FastAPI(lifespan=lifespan)


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


@app.patch("/blueprint/{name}", status_code=201)
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


# Scheduler Methods
@app.post("/scheduler/set/{playlistName}", status_code=201)
def set_job(playlistName: str, every: str, at: str):
    scheduler.add_job(
        fetch,
        args=[playlistName],
        trigger="cron",
        minute=every,
        # hour=at,
        id=playlistName,
        name=playlistName,
        misfire_grace_time=None,  # ensure old schedules are coalesced and runned one time
        replace_existing=True,
    )
    scheduler.export_jobs(schedule_store_path)


@app.post("/schedule/clear/{playlistName}")
def clean_job(playlistName):
    if playlistName == "all":
        scheduler.remove_all_jobs()
    else:
        scheduler.remove_job(playlistName)
    scheduler.export_jobs(schedule_store_path)


@app.get("/scheduler/all")
def get_jobs():
    jobs = []
    joblist = scheduler.get_jobs()
    for job in joblist:
        jobs.append(str(job))
    return list(jobs)


@app.post("/scheduler/{enabled}", status_code=200)
def toggle_scheduler(enabled: bool):
    if enabled:
        scheduler.resume()
    scheduler.pause()


# Heartbeat Method
@app.post("/health")
def heatbeat():
    match scheduler.state:
        case 1:
            return {"Running and processing"}
        case 2:
            return {"Processing Paused"}
        case 0:
            return {"Not Running"}
        case _:
            return {"Status Unknown %s", scheduler.state}


## SCHEDULER RELATED FUNCTIONS


def job_callback(event):
    if event.exception:
        logger.error("Error in job: %s", event.exception)
    else:
        logger.info("Job %s Runned Succesfully", event.job_id)


scheduler.add_listener(job_callback, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)


def import_jobs():
    try:
        scheduler.import_jobs(schedule_store_path, jbs_name)
    except Exception as e:
        logger.error("No schedules found, starting fresh. error: %s", e, exc_info=True)
