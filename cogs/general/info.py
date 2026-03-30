import discord
import datetime
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="credits", aliases=["whomadeyou", "dev"], help="Shows creator of the bot")
    async def credits(self, ctx):
        """Developed by Mohit"""
        msg = (
            "### 🛠️ Developer Credits\n"
            "TaskForge was built with ❤️ by **Mohit**.\n\n"
            "**Links:**\n"
            "• **GitHub:** <https://github.com/Mohit-Mano06/TaskForge-Bot>\n"
            "• **Support:** Check our server for more updates!"
        )
        await ctx.send(msg)

    @commands.command(name="about", aliases=["whoareyou", "bot", "botinfo"], help="Shows information about the bot")
    async def about(self, ctx):
        """Everything about TaskForge"""
        msg = (
            "### 🤖 TaskForge | The High-Performance Assistant\n"
            "Developed by **Mohit** under the **MIT License**.\n\n"
            "**Bot Statistics:**\n"
            f"• **Total Commands:** `{len(self.bot.commands)}` commands loaded\n"
            f"• **Library:** `discord.py` (v{discord.__version__})\n"
            "• **Language:** `Python 3.14.3` (Dedicated Oracle VM)\n\n"
            "*Use `$help` to explore all my capabilities.*"
        )
        await ctx.send(msg)

    @commands.command(name="me", aliases=["whoami", "profile"], help="Shows information about you")
    async def profile(self, ctx, member: discord.Member = None):
        """Your TaskForge Discord Profile"""
        user = member or ctx.author
        
        # Format roles (excluding @everyone) and use .name for "mentions off"
        roles = [role.name for role in user.roles if role != ctx.guild.default_role]
        role_str = ", ".join(roles) if roles else "No roles assigned"

        msg = (
            f"### 👤 {user.display_name}'s Profile\n"
            f"**User:** {user.name} | **ID:** `{user.id}`\n\n"
            "**Server Activity:**\n"
            f"• **Joined Server:** <t:{int(user.joined_at.timestamp())}:R>\n"
            f"• **Account Created:** <t:{int(user.created_at.timestamp())}:R>\n"
            f"• **Top Role:** {user.top_role.name}\n"
            f"• **Roles:** {role_str}"
        )
        await ctx.send(msg)

    @commands.command(name="server", aliases=["serverinfo", "guild"], help="Shows detailed information about the server")
    async def server(self, ctx):
        """Server statistics and information"""
        guild = ctx.guild
        
        # Try to get the owner name safely without mention
        owner = guild.owner or await guild.fetch_member(guild.owner_id)
        owner_name = owner.name if owner else "Unknown Owner"
        
        # Note: online_members requires members intent
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        
        msg = (
            f"### 🌐 Server Information: {guild.name}\n"
            f"**Owner:** {owner_name} | **Created:** <t:{int(guild.created_at.timestamp())}:D>\n\n"
            "**Stats:**\n"
            f"• **Members:** {guild.member_count} ({online_members} online)\n"
            f"• **Channels:** {len(guild.channels)} (Text: {len(guild.text_channels)} | Voice: {len(guild.voice_channels)})\n"
            f"• **Roles:** {len(guild.roles)} total (Mentions Disabled)\n"
            f"• **Server ID:** `{guild.id}`"
        )
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Info(bot))
