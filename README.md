# TaskForge-Bot 🤖 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TaskForge** is a high-performance, AI-integrated Discord bot built with `discord.py`. It transforms your server into a productive and entertaining hub with advanced AI assistants, high-fidelity music streaming, and smart automation.

---

## 🌟 Key Features

### 🧠 TaskForge AI Ecosystem (Powered by Mistral AI)

- **Personal AI Assistant**: Engage in natural, context-aware conversations using `$chat`. TaskForge remembers your last few messages for a truly interactive experience.
- **AI DJ**: Generate custom, high-quality playlists based on your mood, genre, or artist using `$dj`. TaskForge automatically searches and queues the tracks for you.
- **Server Insights & "Obsessions"**: Use `$obsessions` to see what your server is currently hyped about. TaskForge analyzes recent chat trends to find trending topics.
- **Explain Anything**: Use `$explain` to get simplified explanations of complex topics at 4 different levels (Beginner to Expert).
- **Bot Interactions**: Experience witty AI-driven roasts and multi-turn conversations between TaskForge and other bots like Tamabot.

### 🎵 High-Fidelity Music Experience

- **Crystal Clear Audio**: YouTube streaming powered by `yt-dlp` and local `FFmpeg` processing for zero-lag playback.
- **Intelligent Queueing**: Full support for adding, skipping, pausing, and clearing track queues.
- **Voice Stats**: Monitor your voice connection quality in real-time with `$vcstat`.

### ⚡ Smart Productivity & Server Control

- **Dynamic Reminders**: Set personal or voice-channel wide alerts (`$reminder`, `$vcreminder`) with flexible time formats.
- **Advanced Moderation**: A full suite of tools (purge, kick, ban, warn, lock) with cross-server audit logging.
- **System Monitoring**: Keep an eye on bot performance with real-time tracking of RAM, CPU, and Uptime via `$stats`.

---

## ℹ️ Bot Information

- **Library**: `discord.py` (2.3+)
- **Language**: Python 3.12+ (Optimized for 3.14)
- **AI Engine**: Mistral AI (Small & Large models)
- **Audio Engine**: FFmpeg (Local binary supported)

---

## 🛠️ Commands

All commands use the `$` prefix.

### 🤖 AI Assistant & Insights

- `$chat <message>`: Chat with TaskForge AI (uses memory).
- `$resetchat`: Clear your AI conversation history.
- `$explain <level> <topic>`: AI explains a topic. Levels: `1`, `5`, `10`, `engineer`.
- `$obsessions`: Analyzes recent chat history to find trending server topics.
- `$talktamabot`: Start a multi-turn AI conversation with Tamabot.
- `$roasttamabot`: Challenge Tamabot to a savage AI roast battle.
- `$hello`: Get a witty, AI-generated greeting.

### 🎧 Music & AI DJ

- `$dj <request>`: TaskForge AI generates and queues a playlist based on your prompt.
- `$play <search/url>`: Play a song from YouTube or add to queue.
- `$pause` / `$resume`: Control the current track.
- `$skip`: Skip to the next track.
- `$queue`: View the upcoming tracklist.
- `$clear` / `$stop`: Manage or stop the music session.

### 🛡️ Moderation (Admin Only)

- `$purge <amount>`: Fast message cleanup (max 100).
- `$warn <member> [reason]`: Issue a formal warning (logged in `warnings.json`).
- `$kick` / `$ban <member> [reason]`: Securely manage server members.
- `$lock` / `$unlock`: Instantly toggle channel sending permissions.

### ⏰ Reminders & Productivity

- `$reminder <time> <message>`: Personal reminder (e.g., `$reminder 30m Take a break`).
- `$vcreminder <time> <message>`: Alert everyone in your current voice channel.
- `$vcmembers`: Quickly list all active members in your Voice Channel.

### 🛠️ Utilities & Voice

- `$ping`: Check API & WebSocket latency with humorous diagnostics.
- `$stats`: View technical environment stats (RAM, CPU, Uptime).
- `$roll`: Roll a standard 6-sided dice.
- `$vcstat`: Detailed voice connection quality and stats.
- `$connect` / `$disconnect`: Manage the bot's voice presence.

### 📩 Social & Fun

- `$confess <message>`: Send an anonymous message to the designated confession channel.

### ℹ️ Information

- `$about` (aliases: `bot`, `botinfo`): Comprehensive breakdown of TaskForge's mission and stats.
- `$me` (aliases: `profile`, `whoami`): Your detailed Discord profile with role listing and timestamps.
- `$server` (aliases: `serverinfo`, `guild`): Full server statistics, including member counts and channel breakdowns.
- `$credits` (aliases: `dev`, `whomadeyou`): Recognition of the bot's developers and project links.
- `$setupguide`: Detailed deployment instructions for developers.

---

## ⚙️ Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Mohit-Mano06/TaskForge-Bot.git
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:

   Create a `.env` file in the root directory:

   ```env
   TOKEN=your_discord_bot_token
   MISTRAL_TOKEN=your_mistral_api_key
   ```

4. **FFmpeg Setup**:

   Ensure `ffmpeg.exe` is in your system PATH or located in `cogs/music/ffmpeg/`.

5. **Run the Bot**:

   ```bash
   ./start.bat
   ```

---

*Developed with ❤️ by [Mohit](https://github.com/Mohit-Mano06)*
