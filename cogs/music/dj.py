import asyncio
import re 
import os

from discord.ext import commands
from mistralai.client import Mistral

def make_progress_bar(current, total, length=12):
    """Generates a stylish ASCII progress bar"""
    if total <= 0:
        return "□" * length
    # Clamp the ratio between 0 and 1
    ratio = min(max(current / total, 0), 1)
    filled = int(length * ratio)
    return "■" * filled + "□" * (length - filled)

class AIDJ(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.client = Mistral(api_key=os.getenv("MISTRAL_TOKEN"))

        self.dj_prompt = """
        You are an AI DJ.

        Your task is to generate a playlist based on the user's music request.

        First interpret the request and extract:
        - count: number of songs requested (default 5)
        - artist: artist name if mentioned
        - genre: genre if mentioned
        - priority: latest / top / hit / none

        Song selection logic:

        If priority is "top" or "hit":
        - Choose the artist's most popular and widely recognized songs.
        - Prefer songs that were viral, charting, or widely streamed.
        - Prioritize songs used in popular movies, trending reels, or known by most listeners.

        If priority is "latest":
        - Prefer songs released in the last few years.

        General rules:
        - If an artist is specified, only include songs from that artist.
        - Avoid obscure or deep-cut songs unless the user explicitly asks for them.
        - Only include real official songs, not playlists, mashups, or compilations.
        - Prefer songs with hundreds of millions of streams or widely recognized hits.

        Output rules:
        - Format exactly: Artist - Song
        - One song per line
        - No numbering
        - No explanations
        - No extra text
        """
    
    def extract_song_count(text):
        match = re.search(r"\b(\d+)\b", text)
        if match:
            return int(match.group(1))
        return 5

    @commands.command()
    async def dj(self, ctx, *, question: str):
        """AI DJ Command - Generates and plays a themed playlist"""

        async with ctx.typing():
            try:
                response = await self.client.chat.complete_async(
                    model="open-mistral-7b",
                    messages=[
                        {"role": "system", "content": self.dj_prompt},
                        {"role": "user", "content": question}
                    ]
                )

                songs_text = response.choices[0].message.content
                songs = [s.strip() for s in songs_text.split("\n") if s.strip()]

                if not songs:
                    return await ctx.send("❌ I couldn't generate any songs for that request.")

                # Fancy ASCII Box Formatting (Integrated from draft)
                msg = "╭─ 🎧 TASKFORGE AI DJ\n"
                msg += f"│ Request : {question}\n"
                msg += "│ Playlist:\n│\n"

                for i, song in enumerate(songs, 1):
                    msg += f"│ {i}. {song}\n"

                msg += "╰────────────────────"
                await ctx.send(f"```\n{msg}\n```")

                # Play the generated songs
                play_command = self.bot.get_command("play")
                if not play_command:
                    return await ctx.send("❌ The `play` command is not available.")
                total = len(songs)

                progress_msg = await ctx.send("🎧 Preparing the DJ magic...")

                for i, song in enumerate(songs, 1):

                    clean_song = re.sub(r'^[\d\.\-\)\•]+\s*', '', song).strip()

                    if "-" in clean_song:
                        artist, title = clean_song.split("-", 1)
                        artist = artist.strip()
                        title = title.strip()

                        search_query = f"ytsearch1:{artist} {title} official video"
                    else:
                        search_query = f"ytsearch1:{clean_song} official audio"

                    bar = make_progress_bar(i, total)

                    msg = (
                        "╭─ 🎧 TASKFORGE AI DJ\n"
                        "│ Queueing songs...\n"
                        "│\n"
                        f"│ Progress: [{bar}] {i}/{total}\n"
                        f"│ Adding: {clean_song}\n"
                        "╰────────────────────"
                    )

                    await progress_msg.edit(content=f"```\n{msg}\n```")

                    await ctx.invoke(play_command, search=search_query)

                    await asyncio.sleep(1)

            except Exception as e:
                await ctx.send(f"❌ An error occurred: {str(e)}")


async def setup(bot):
    await bot.add_cog(AIDJ(bot))
