import random
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Shows creator of the bot")
    async def whomadeyou(ctx):
        await ctx.send("I was made by Momo ;) ")

    @commands.command(help = "Shows info about the bot")
    async def whoareyou(ctx):
        await ctx.send("Am a simple discord bot created by Momo")

    @commands.command(help = "Shows Github Repo link for development")
    async def botinfo(ctx):
        embed = discord.Embed(
            title="Bot Info",
            color=discord.Color.blue()
        )
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Total Commands", value=len(self.bot.commands), inline=True)

        await ctx.send(embed=embed)

        
async def setup(bot):
    await bot.add_cog(Info(bot))
