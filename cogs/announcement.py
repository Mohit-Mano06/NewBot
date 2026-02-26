import discord
from discord.ext import commands
from discord import app_commands
from cogs.admin.config import DEV_GUILD_ID, ANNOUNCEMENT_CHANNEL_ID, OWNER_ID


class Announcement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="announce")
    @commands.is_owner()
    async def announce(self, ctx: commands.Context, *, message: str = None):
        if not message:
            await ctx.send("Please provide an announcement message.", delete_after=5)
            return

        if ctx.guild.id != DEV_GUILD_ID:
            return await ctx.send("You can't use this command here!", delete_after=5)

        try: 
            channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL_ID) or await self.bot.fetch_channel(ANNOUNCEMENT_CHANNEL_ID)

            embed = discord.Embed(
                title = "🚀 New TaskForge Update",
                description=message,
                color = discord.Color.blue(),
                timestamp = discord.utils.utcnow()
            )

            embed.set_footer(text="TaskForge Bot")

            await channel.send(embed = embed)
            await ctx.send("✅ Announcement sent successfully!", delete_after=5)

        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}", delete_after=10)


async def setup(bot: commands.Bot):
    await bot.add_cog(Announcement(bot))
    