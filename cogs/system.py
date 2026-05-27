import psutil
import os
import time
from discord.ext import commands



class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()


    @commands.command()
    async def stats(self, ctx):
        """Shows bot statistics"""
        
        process = psutil.Process(os.getpid())

        ram = process.memory_info().rss / (1024 ** 2)
        cpu = process.cpu_percent(interval = 1)
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        else:
            uptime_str = f"{minutes}m {seconds}s"

        await ctx.send(
            f"⚙️ **Bot Stats**\n"
            f"🧠 RAM: `{ram:.2f} MB`\n"
            f"💻 CPU: `{cpu}%`\n"
            f"⏱️ Uptime: `{uptime_str}`"
        )

async def setup(bot):
    await bot.add_cog(System(bot))