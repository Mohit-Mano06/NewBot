# TaskForge-Bot🤖

A high-performance Discord bot built with Python and `discord.py`, developed by **Momo** (Mohit & Anis). This bot handles everything from server utilities and moderation to high-quality music playback.

## Features ✨

- **Music Player**: High-fidelity YouTube streaming with queue support and local FFmpeg processing.
- **AI DJ**: Mistral AI-powered playlist generation based on mood, genre, or specific requests.
- **AI Bot Interaction**: Multi-turn conversations and roast battles with other bots (like Tamabot) using Mistral AI.
- **System monitoring**: Real-time tracking of RAM, CPU, and Uptime.
- **Moderation Toolset**: Advanced commands for server management including purge, kick, ban, warn, and channel locking.
- **Multi-Server Logging**: Intelligent, automated logging system that routes moderation events to server-specific channels.
- **Reminders**: Set personal or voice channel-wide reminders with natural time formats.
- **Announcements**: Broadcast version updates and news with dedicated embeds (Owner only).
- **Confessions**: Safely share anonymous messages in server-specific channels.
- **Utilities**: Advanced latency monitoring, dice rolling, and voice connection stats.

## Bot Information ℹ️

- **Developers**: Momo [Mohit](https://github.com/Mohit-Mano06)
- **Library**: discord.py
- **Language**: Python 3.12+ (Currently run on 3.14.3)
- **Audio Engine**: FFmpeg (Local binary supported)
- **Security**: Role-based permissions (is_bot_admin check)

## Commands 🛠️

The bot uses the `$` prefix for all commands.

### 🤖 AI & Bot Interaction

- `$dj <request>`: Uses Mistral AI to generate and queue a playlist based on your prompt.
- `$talktamabot [message]`: Start an interactive multi-turn conversation with Tamabot.
- `$roasttamabot`: Challenges Tamabot to a roast battle.

### 🎵 Music

- `$play <search/url>`: Plays a song from YouTube or adds it to the queue.
- `$pause`: Pauses the current track.
- `$resume`: Resumes the paused track.
- `$skip`: Skips to the next song in the queue.
- `$clear`: Clears the current music queue.
- `$stop`: Stops the music and clears the queue.
- `$queue`: Shows the current upcoming tracks.

### 🛡️ Moderation (Admin Only)

- `$purge <amount>`: Cleans up a specified number of messages (max 100).
- `$kick <member> [reason]`: Kicks a member from the server and logs the action.
- `$ban <member> [reason]`: Permanently bans a member and logs the action.
- `$warn <member> [reason]`: Issues a formal warning to a member.
- `$lock`: Locks the current channel, preventing members from sending messages.
- `$unlock`: Unlocks the current channel, restoring message permissions.

### ⏰ Reminders

- `$reminder <time> <message>`: Set a personal reminder (e.g., `$reminder 10m Coffee break`).
- `$vcreminder <time> <message>`: Remind everyone in your current voice channel.
- `$vcmembers`: Quick list of everyone currently in your voice channel.

### 📢 Announcements (Owner Only)

- `$announce <version> <type> <message>`: Send a new release announcement.
- `$latest`: View details of the most recent bot update.

### 🛠️ Utilities

- `$ping`: Advanced latency check (API & WebSocket response times).
- `$stats`: Check bot technical statistics (RAM, CPU, Uptime).
- `$roll`: Roll a standard 6-sided dice.
- `$setupguide`: Access detailed instructions for bot setup and deployment.

### 📩 Confessions

- `$confess <message>`: Post an anonymous message to the confession channel (aliases: `$confession`).

### ℹ️ Information

- `$botinfo`: Technical stats about the bot's environment and command count.
- `$serverinfo`: View detailed information about the current Discord server.
- `$whoami`: Display your Discord profile details (ID, Join Date, Avatar).
- `$whomadeyou`: Credits for the bot's creators.
- `$whoareyou`: A brief intro to the bot's purpose.

### 🔊 Voice

- `$connect`: Bring the bot into your voice channel.
- `$disconnect`: Make the bot leave voice.
- `$vcstat`: Check voice connection quality and member stats.

## Installation & Setup ⚙️

1. **Clone the repo**:

    ```bash
    git clone https://github.com/Mohit-Mano06/TaskForge-Bot.git
    ```

2. **Install requirements**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure FFmpeg**:

    Place your `ffmpeg.exe` in `cogs/music/ffmpeg/` or ensure it's in your system PATH.

4. **Logging Setup**:

    Configure your Guild and Channel IDs in `cogs/admin/logging.py` to enable cross-server logging.

5. **Environment Variables**:

    Create a `.env` file with your `TOKEN` and `MISTRAL_TOKEN`.

6. **Run the bot**:

    ```bash
    ./start.bat
    ```
