import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import urllib.parse
import urllib.request
import re

def search_youtube(query):
    """Fallback manual HTML scraper for YouTube search to bypass datacenter blocking."""
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(
            search_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        html = urllib.request.urlopen(req).read().decode()
        
        # Look for the videoId in the page's JSON data objects
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if not video_ids:
            # Fallback to standard watch URL patterns if JSON structure changes
            video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
            
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        print(f"[Manual Search Error] {e}")
    return None


# FFmpeg: auto-detect system binary (Linux/Ubuntu) or local exe (Windows)
current_dir = os.path.dirname(os.path.abspath(__file__))
_local_ffmpeg = os.path.join(current_dir, "ffmpeg", "ffmpeg.exe")
FFMPEG_EXE_PATH = _local_ffmpeg if os.path.isfile(_local_ffmpeg) else "ffmpeg"

# cookies.txt: check project root first, then cogs/music/, skip if neither found
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
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'cookiefile': COOKIES_PATH,
    'source_address': '0.0.0.0',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    },
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -ar 48000 -ac 2',
}


def get_ytdl(client="android"):
    """Returns a YoutubeDL instance configured with a specific player client."""
    opts = ytdl_format_options.copy()
    opts['extractor_args'] = {'youtube': [f'player_client={client}']}
    return yt_dlp.YoutubeDL(opts)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()

        def extract():
            target_url = url
            
            # 🔥 1. FORCE MANUAL SEARCH (If not a URL)
            if not target_url.startswith("http"):
                print(f"[Search Engine] Performing manual scrape for query: {target_url}")
                target_url = search_youtube(url)
                if not target_url:
                    raise ValueError("Manual search failed: YouTube returned no results or blocked the request")

            # 🔥 2. MULTI-CLIENT EXTRACTION
            clients = ["android", "web", "ios"]
            data = None
            last_error = None

            for client in clients:
                try:
                    print(f"[Extractor] Attempting extraction with client '{client}' on {target_url}")
                    ydl = get_ytdl(client)
                    data = ydl.extract_info(target_url, download=not stream)
                    if data:
                        print(f"[Extractor] Success with client '{client}'")
                        break
                except Exception as e:
                    print(f"[Extractor] Client '{client}' failed: {e}")
                    last_error = str(e)

            if not data:
                raise ValueError(f"yt-dlp failed to extract data from all clients. Last error: {last_error}")

            # Extract from playlist structure if applicable
            if 'entries' in data:
                entry = next((e for e in data['entries'] if e), None)
                if not entry:
                    raise ValueError("No valid entries found in the playlist/search result")
                data = entry

            # 🔥 3. ROBUST STREAM URL EXTRACTION
            stream_url = data.get('url')

            if not stream_url:
                formats = data.get('formats', [])
                if not formats:
                    raise ValueError("Could not extract stream URL: No formats present in data payload")

                # Step 3a: Audio-only preference
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and (f.get('vcodec') == 'none' or not f.get('vcodec')) and f.get('url')]
                
                # Step 3b: Any format with audio
                if not audio_formats:
                    audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]
                    
                # Step 3c: Ultimate fallback (any format with URL)
                if audio_formats:
                    stream_url = audio_formats[-1]['url']
                else:
                    valid_formats = [f for f in formats if f.get('url')]
                    if not valid_formats:
                        raise ValueError("No playable formats found")
                    stream_url = valid_formats[-1]['url']

            if not stream_url:
                raise ValueError("Stream extraction failed inexplicably after fallback parsing")

            return stream_url, data

        stream_url, data = await loop.run_in_executor(None, extract)

        return cls(
            discord.FFmpegPCMAudio(
                stream_url,
                executable=FFMPEG_EXE_PATH,
                **ffmpeg_options
            ),
            data=data
        )
    
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
                    source = await asyncio.wait_for(self.queue.get(), timeout=300)  # 5 minutes idle timeout
                except asyncio.TimeoutError:
                    return self.destroy(self._guild)

                self.current = source
                print(f"[Player] Got source: {source.title}")

                # Wait up to 10 seconds for the VC connection to finalize
                wait_time = 0
                while wait_time < 10 and self.vc and not self.vc.is_connected():
                    await asyncio.sleep(1)
                    wait_time += 1

                if not self.vc or not self.vc.is_connected():
                    print("[Player] Not connected to VC, destroying player.")
                    return self.destroy(self._guild)

                try:
                    def after_play(error):
                        if error:
                            print(f"[Player Error] Playback error: {error}")
                        # Always unblock the loop — even on error, or queue hangs forever
                        self.bot.loop.call_soon_threadsafe(self.next.set)

                    self.vc.play(source, after=after_play)
                except Exception as e:
                    import traceback
                    print(f"[Player Exception when calling play()] {e}")
                    traceback.print_exc()
                    self.next.set()  # unblock even on exception

                await self._channel.send(f"🎵 **Now playing:** `{source.title}`")

                await self.next.wait()

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
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = GuildPlayer(ctx)
            player._cog = self  # Ensure it always belongs to MusicPlayer, even if invoked by AI DJ
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

        try:
            if ctx.voice_client:
                if not ctx.voice_client.is_connected():
                    # Zombie connection detected, force disconnect first
                    await ctx.voice_client.disconnect(force=True)
                    player.vc = await ctx.author.voice.channel.connect(timeout=60.0)
                else:
                    player.vc = ctx.voice_client
            else:
                player.vc = await ctx.author.voice.channel.connect(timeout=60.0)
        except Exception as e:
            # Catches discord.errors.ClientException and TimeoutError
            print(f"[Player Error] VC Connect Exception: {e}")
            return await ctx.send(f"❌ Failed to join the voice channel: `{str(e)}`")

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
        msg += f"│ Now Playing: {player.current.title}\n" if player.current else "│ Now Playing: Nothing\n"
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
            if member.guild.id in self.players:
                await self.cleanup_player(member.guild)


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
