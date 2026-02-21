# 🌉 Terabithia

[![STATUS](https://img.shields.io/badge/Status-BETA-orange?style=for-the-badge&logo=as&logoColor=white)](https://www.navidrome.org/)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/license/MIT)

**Terabithia** is a lightweight and simple music discovery and automated downloader designed for self-hosted systems. While tested with [Navidrome](https://www.navidrome.org/), it should remain completely system-agnostic, bridging the gap between online music discovery and your local library.


[Features](#-features) • [How it Works](#-how-it-works) • [Installation](#-installation) • [Usage](#-usage) • [API Reference](https://github.com/moddroid94/terabithia/wiki/API-Interface-Reference)

---
## STATUS:

This repo explains the objective of the project, but does not contain all the features **yet**.

The functioning features as of now are:
- Listenbrainz API integration with:
    - Radio suggestions from track, album, artist or genres
- FLAC Audio Downloads from multiple hifi API source
- Tagging with artwork from hifi API metadata source
- Custom playlist generation
- Persistent jobs schedule with sqlite
- Health check endpoint for scheduler state
- WebUI scheduling and managment interface

In Development:
- [x] yaml Config file prompts and config
- [x] API-Agnostic interface
- [x] Retry-Logic for API requests (lbz)
- [x] Independent logging for main loop, scheduler thread and runner processes
- [x] WebUI Frontend
- [ ] UI Configurable folder paths
- [ ] UI Editable User config

<br>
<br>

## ✨ Features (WIP)

- 🧠 **Smart Discovery**: Get recommendations based on multiple API sources and prompts.
- 🔍 **Automated Matching**: Searches and matches tracks across Audio API sources.
- 💾 **Seamless FLAC Downloader**: Downloads FLAC files and organizes them into folders.
- 🏷️ **Clean Tagging**: Automatically applies Vorbis tags from the audio source to keep track consistency and your library accurate.
- 🎼 **Playlist Generation**: Creates standard relative `.m3u8` files for instant import into Navidrome or any other player.
- ⏲️ **Persistent Fault Tolerant Scheduler**: Schedule based on cron or simple intervals, automatically coalesce missed runs, store on SQlite DB.
- 🪵 **Exhaustive logs**: We love nature, logs are thread specific and level can be set easily from config, No tree harmed.
- 🛠️ **System Agnostic**: Works on any filesystem; if your player can read a folder, it can use Terabithia.
- 🕹️ **Pluggable API**: Common interfaces allows to add source APIs with ease (for devs).

<br>

# Screenshots:

![home page][home]
![schedules][sched]
![reports][runs]
<br>

## ⚙️ How it Works

Terabithia acts as a bridge betweem your self-hosted music ecosystem and online music services:

1.  **Input**: You provide a seed list (listenbrainz user history, similar track, artist, album or genre, based on API availablility).
2.  **API Discovery**: The app queries the APIs to generate a list of suggested tracks.
3.  **API Acquisition**: It finds the best matches from the available APIs and downloads the audio.
4.  **Organization**: Tracks are tagged and moved to `Artist/Album/Track.ext`.
5.  **Integration**: A m3u8 playlist file is generated at the root folder level, with relative file paths, ready for your server or player to scan.

### Some of the tools used in this app:
- mutagen
- hifiaudioapi (API Only)
- music-tag (artwork write only)
- APScheduler
- custom fork of liblistenbrainz
- FastAPI
- Vite
- sqlalchemy
- musicbrainzngs
---

## 🚀 Installation

### Prerequisites
- Python 3.12+
- uv
- bun

---

## 🛠 Usage

**Right now only implements the radio API for listenbrainz.
follow the prompt guideline here for config prompt generation [Radio API](https://troi.readthedocs.io/en/latest/lb_radio.html)** 

### Setup
```bash
# Clone the repository
git clone https://github.com/moddroid94/terabithia.git
cd terabithia
```

### Configuration:

Create a config.json from the example in the repo, then run.

### Run:
Run the backend with 3 simple commands:
```bash
cd backend
# install deps
uv sync
# run
uv run fastapi run main.py 
```
Run the frontend with another terminal and 3 simple commands:
```bash
cd frontend
# install deps
bun install
# run
bun run dev
```

---
## API Availability:
  - AudioAPI: hifi
  - MetaAPI: lbz (Listenbrainz)

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

# Disclaimer
The author(s) of this project are not responsible for how you use the app. Users are solely responsible for ensuring their use of the app complies with applicable laws and terms of service. This software is provided "as is" without warranty of any kind.

## 📄 License

Distributed under the MIT License. See `LICENSE.md` for more information.

---
<p align="center">
  Built with ❤️ for the self-hosted community.
</p>

[home]: images/image.png
[sched]: images/image-1.png
[runs]: images/image-2.png
