import discord
import datetime
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Shows creator of the bot")
    async def whomadeyou(self, ctx):
        await ctx.send("I was made by Momo ;) ")

    @commands.command(help = "Shows info about the bot")
    async def whoareyou(self, ctx):
        await ctx.send("Am a simple discord bot created by Momo")

    @commands.command(help = "Shows information about bot")
    async def botinfo(self, ctx):
        embed = discord.Embed(
            title="Bot Info",
            color=discord.Color.blue()
        )
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Total Commands", value=len(self.bot.commands), inline=True)

        await ctx.send(embed=embed)
    @commands.command(help = "Shows info about you")
    async def whoami(self,ctx):
        user = ctx.author

        msg = (
            f"Username: {user.name}\n"
            f"ID: {user.id}\n"
            f"Joined at: {user.joined_at}\n"
            f"Avatar URL: {user.display_avatar.url}\n"
            )

        await ctx.send(msg)

    @commands.command(name="serverinfo", help="Shows detailed information about the server")
    async def serverinfo(self, ctx):
        guild = ctx.guild

        embed = discord.Embed(
            title="🌐 SERVER INFO",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="📛 Name", value=guild.name, inline=True)
        embed.add_field(name="👑 Owner", value=guild.owner, inline=True)
        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%d %b %Y"), inline=True)

        footer_icon = self.bot.user.display_avatar.url if self.bot.user.avatar else None
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=footer_icon)

        await ctx.send(embed=embed)

    @commands.command(help = "Shows bot uptime")
    async def uptime(self, ctx):
        uptime = datetime.datetime.now(datetime.timezone.utc) - self.bot.start_time
        uptime = str(uptime).split('.')[1] if '.' in str(uptime) else str(uptime) # Remove microseconds
        # Actually split is better:
        uptime_str = str(uptime).split('.')[0]
        await ctx.send(f"Current Uptime: {uptime_str}")

        
async def setup(bot):
    await bot.add_cog(Info(bot))
