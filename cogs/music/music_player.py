import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import wavelink 

# FFmpeg path: use system ffmpeg on Linux (Oracle VM), fallback to local exe on Windows
current_dir = os.path.dirname(os.path.abspath(__file__))
_local_ffmpeg = os.path.join(current_dir, "ffmpeg", "ffmpeg.exe")
FFMPEG_EXE_PATH = _local_ffmpeg if os.path.isfile(_local_ffmpeg) else "ffmpeg"

# cookies.txt — check project root first, then cogs/music/, skip if neither exists
_project_root = os.path.dirname(os.path.dirname(current_dir))
_root_cookies = os.path.join(_project_root, "cookies.txt")
_local_cookies = os.path.join(current_dir, "cookies.txt")
if os.path.isfile(_root_cookies):
    COOKIES_PATH = _root_cookies
elif os.path.isfile(_local_cookies):
    COOKIES_PATH = _local_cookies
else:
    COOKIES_PATH = None


# YTDL Configuration
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
<<<<<<< Updated upstream
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile' : os.path.join(BASE_DIR, '..', 'data', 'cookies.txt')
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    },
    'age_limit' : 99,
=======
    'ignoreerrors': False,   # keep False so errors surface; we handle None data explicitly
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'cookiefile': COOKIES_PATH if os.path.isfile(COOKIES_PATH) else None,
    'source_address': '0.0.0.0',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    },
>>>>>>> Stashed changes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -ar 48000 -ac 2',
}


def get_ytdl():
    return yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: get_ytdl.extract_info(url, download=not stream))

        if data is None:
            raise ValueError("yt-dlp returned no data. The video may be unavailable, age-restricted, or region-blocked.")

        if 'entries' in data:
            # Playlist — grab the first valid entry
            entry = next((e for e in data['entries'] if e), None)
            if entry is None:
                raise ValueError("No valid entries found in the playlist/search result.")
            data = entry

        if not data.get('url'):
            raise ValueError(f"Could not extract a stream URL for: {data.get('title', url)}")

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable=FFMPEG_EXE_PATH, **ffmpeg_options), data=data)

class GuildPlayer:
    """A class which is assigned to each guild using the bot for Music."""
    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'vc')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.vc = None
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop."""
        await self.bot.wait_until_ready()

        try:
            while not self.bot.is_closed():
                self.next.clear()

                try:
                    # Wait for the next song. If we timeout cancel the player and leave...
                    async with asyncio.timeout(300):  # 5 minutes
                        source = await self.queue.get()
                except (asyncio.TimeoutError, TimeoutError):
                    return self.destroy(self._guild)

                self.current = source
                print(f"[Player] Got source: {source.title}")

                # Ensure we are actually connected...
                if not self.vc or not self.vc.is_connected():
                    print("[Player] Not connected to VC, destroying player.")
                    return self.destroy(self._guild)

                try:
                    def after_play(error):
                        if error:
                            print(f"[Player Error] Playback error: {error}")
                        # Always signal next, whether there was an error or not —
                        # otherwise the loop hangs forever waiting on self.next.wait()
                        self.bot.loop.call_soon_threadsafe(self.next.set)

                    self.vc.play(source, after=after_play)
                except Exception as e:
                    import traceback
                    print(f"[Player Exception when calling play()] {e}")
                    traceback.print_exc()
                    self.next.set()  # unblock the loop even on exception

                await self._channel.send(f"🎵 **Now playing:** `{source.title}`")

                await self.next.wait()

                # Make sure the FFmpeg process is cleaned up.
                source.cleanup()
                self.current = None
        except Exception as e:
            import traceback
            print(f"[Player Fatal Error] {e}")
            traceback.print_exc()
            self.destroy(self._guild)

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup_player(guild))

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        """Retrieve the guild player, or create one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = GuildPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    async def cleanup_player(self, guild):
        """Cleanup a single guild's player."""
        try:
            player = self.players.pop(guild.id)
            if player.vc:
                await player.vc.disconnect()
        except KeyError:
            pass

    @commands.command(name='play', help='Plays a song from YouTube')
    async def play(self, ctx, *, search: str):
        """Streams from a query (YouTube search or URL)."""
        if not ctx.author.voice:
            return await ctx.send("❌ You must be in a voice channel to play music!")

        player = self.get_player(ctx)

        if not player.vc or not player.vc.is_connected():
            player.vc = await ctx.author.voice.channel.connect()

        async with ctx.typing():
            try:
                source = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True)
                await player.queue.put(source)
            except Exception as e:
                return await ctx.send(f"❌ An error occurred: {str(e)}")

        if player.vc.is_playing() or not player.queue.empty():
            if player.current != source:
                await ctx.send(f"✅ Added to queue: `{source.title}`")

    @commands.command(name='pause', help='Pauses the current song')
    async def pause(self, ctx):
        player = self.get_player(ctx)
        if player.vc and player.vc.is_playing():
            player.vc.pause()
            await ctx.send("⏸️ Paused.")

    @commands.command(name='resume', help='Resumes the current song')
    async def resume(self, ctx):
        player = self.get_player(ctx)
        if player.vc and player.vc.is_paused():
            player.vc.resume()
            await ctx.send("▶️ Resumed.")

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        player = self.get_player(ctx)
        if player.vc and player.vc.is_playing():
            player.vc.stop()
            await ctx.send("⏭️ Skipped.")

    @commands.command(name='stop', help='Stops music and leaves the VC')
    async def stop(self, ctx):
        player = self.get_player(ctx)
        if player.vc:
            await self.cleanup_player(ctx.guild)
            await ctx.send("⏹️ Stopped and disconnected.")

    @commands.command(name='queue', help='Shows the current music queue')
    async def queue_info(self, ctx):
        player = self.get_player(ctx)

        if not player.current and player.queue.empty():
            return await ctx.send("🎧 The queue is currently empty.")

        upcoming = list(player.queue._queue)

        msg = "╭─ 🎵 MUSIC QUEUE\n"
        if player.current:
            msg += f"│ Now Playing: {player.current.title}\n"
        else:
            msg += "│ Now Playing: Nothing\n"

        msg += "│\n"

        if not upcoming:
            msg += "│ No upcoming songs.\n"
        else:
            msg += "│ Upcoming:\n"
            for i, song in enumerate(upcoming, 1):
                msg += f"│ {i}. {song.title}\n"

        msg += "╰────────────────────"

        await ctx.send(f"```\n{msg}\n```")

    @commands.command(name="clear", help="Clears the music queue")
    async def clear(self, ctx):
        player = self.get_player(ctx)

        if player.queue.empty():
            return await ctx.send("Queue is already empty.")

        player.queue = asyncio.Queue()

        await ctx.send("🧹 Queue cleared.")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates to cleanup players if bot is disconnected."""
        if member == self.bot.user and after.channel is None:
            # Bot was disconnected
            if member.guild.id in self.players:
                await self.cleanup_player(member.guild)

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
