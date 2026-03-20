# 📂 Project Structure Guide

This document outlines the folder structure and the purpose of each file in the **TaskForge-Bot** project.

## 📌 Root Directory

| File / Folder | Description |
| -------------- | ------------- |
| `main.py` | Entry point. Handles startup, extension loading, and global error handling. |
| `.env` | **Secret**. Contains `TOKEN` and `MISTRAL_TOKEN`. Do not commit! |
| `config_example.py` | Template for environment variable setup. |
| `requirements.txt` | Python library dependencies. |
| `README.md` | Setup instructions and feature overview. |
| `logger.py` | Specialized logging utility for moderation events. |
| `start.bat` | Windows batch script to launch the bot in the virtual environment. |

---

## ⚙️ Cogs Directory (`/cogs`)

Modular extensions grouped by functionality.

### 📁 `cogs/general/`

Core utility and information commands.

- `info.py`: Bot/Server information, whoami, and uptime.
- `utility.py`: General tools (ping, roll) and voice connection stats.
- `confession.py`: Anonymous messaging system.
- `announcement.py`: Versioning and update broadcasts.
- `status.py`: Automated bot status (presence) cycling.
- `setupguide.py`: Developer setup instructions.

### 📁 `cogs/mistral/`

AI-powered features leveraging the Mistral SDK.

- `ai.py`: AI DJ and playlist generation.
- `bot_chat/`: Multi-turn AI conversation system and bot-to-bot roasts.
  - `chat.py`: Core conversation logic and Tamabot interaction.
  - `memory.py`: (Optional/Internal) Handles conversation state.

### 📁 `cogs/music/`

Core music playback engine.

- `music_player.py`: yt-dlp based audio streaming with FFmpeg.
- `ffmpeg/`: Local FFmpeg binaries for cross-platform support.

### 📁 `cogs/admin/`

Server management and security.

- `moderation.py`: Kick, ban, purge, warn, and logging integration.
- `logging.py`: Cross-server moderation event logging.
- `config.py`: Configuration for administrative roles and channels.

### 📁 `cogs/reminder/`

Time-based alerting systems.

- `reminder.py`: User-facing personal reminders.
- `vcreminder.py`: Voice channel-wide alerts and member tracking.

### ⚙️ System Cog (`cogs/system.py`)

- `system.py`: Real-time monitoring of bot performance (CPU, RAM, Uptime).
