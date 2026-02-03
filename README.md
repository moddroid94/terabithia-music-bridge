# 🌉 Terabithia

[![STATUS](https://img.shields.io/badge/Status-BETA-orange?style=for-the-badge&logo=as&logoColor=white)](https://www.navidrome.org/)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Built for Navidrome](https://img.shields.io/badge/Built_for-Navidrome-orange?style=for-the-badge&logo=navidrome&logoColor=white)](https://www.navidrome.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/license/MIT)

**Terabithia** is a lightweight and simple music discovery and automated downloader designed for self-hosted systems. While tested with [Navidrome](https://www.navidrome.org/), it should remain completely system-agnostic, bridging the gap between online music discovery and your local library.


[Features](#-features) • [How it Works](#-how-it-works) • [Installation](#-installation) • [Usage](#-usage)

---
## STATUS:

This repo explains the objective of the project, but does not contain all the features **yet**.

The functioning features as of now are:
- Listenbrainz API integration with:
    - recommendations for user
    - radio plylist from track, album, artist or genres
- FLAC Audio Downloads from multiple hifi API source
- Tagging with artwork from hifi API metadata source
- Playlist generation

In Development:
- [ ] yaml Config file prompts and config
- [ ] Complete API-Agnostic interface
- [ ] Full Retry-Logic for API requests
- [ ] Configurable folder paths
- [ ] Complete logging and error handling

---

## ✨ Features (WIP)

- 🧠 **Smart Discovery**: Get recommendations based on multiple API sources and custom prompts.
- ⚙️ **Multi Playlist Generation**: Generates multiple playlists based on the prompt list. 
- 🕹️ **Pluggable API**: Common interfaces allows to expand the API with ease.
- 🔍 **Automated Matching**: Searches and matches tracks across Audio API sources.
- 💾 **Seamless FLAC Downloader**: Downloads FLAC files and organizes them into your library's folder structure.
- 🏷️ **Clean Tagging**: Automatically applies Vorbis tags from the audio source to keep track consistency and your library accurate.
- 🎼 **Playlist Generation**: Creates standard relative `.m3u8` files for instant import into Navidrome or any other player.
- 🛠️ **System Agnostic**: Works on any filesystem; if your player can read a folder, it can use Terabithia.

---

## ⚙️ How it Works

Terabithia acts as a bridge betweem your self-hosted music ecosystem and online music services:

1.  **Input**: You provide a seed list (listenbrainz user history, similar track, artist, album or genre, based on API availablility).
2.  **API Magic**: The app queries the APIs to generate a list of suggested tracks.
3.  **Acquisition**: It finds the best matches from the available APIs and downloads the audio.
4.  **Organization**: Tracks are tagged and moved to `Artist/Album/Track.ext`.
5.  **Integration**: A m3u8 playlist file is generated at the root folder level, with relative file paths, ready for your server or player to scan.

---

## 🚀 Installation

### Prerequisites
- Python 3.9+
- uv

### Setup
```bash
# Clone the repository
git clone https://github.com/moddroid94/terabithia.git
cd terabithia

# Install dependencies
uv sync
```

---

## 🛠 Usage

Run the tool with a simple command to start the process:

**WIP: Right now it fetches and builds a single playlist in the root folder of the project, with tracks from unlistened user (myself) recommendations, you can change the prompt with something else, following the API specs for the radio mix on listebrainz.** 


```bash
# run
uv run main.py 
```

### Configuration
Soon i'll add a config yaml, right now it's all hardcoded in the main.py main funciton.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE.md` for more information.

---
<p align="center">
  Built with ❤️ for the self-hosted community.
</p>