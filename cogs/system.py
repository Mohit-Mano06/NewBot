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
        uptime = time.time() - self.start_time

        await ctx.send(
            f"⚙️ **Bot Stats**\n"
            f"🧠 RAM: `{ram:.2f} MB`\n"
            f"💻 CPU: `{cpu}%`\n"
            f"⏱️ Uptime: `{uptime:.0f}s`"
        )

async def setup(bot):
    await bot.add_cog(System(bot))