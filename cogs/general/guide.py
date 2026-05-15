import discord
from discord.ext import commands

class SetupGuide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setupguide(self, ctx):

        embed1 = discord.Embed(
            title="🚀 TaskForge Bot | Setup Guide",
            description="Follow these steps to run the bot locally.",
            color=discord.Color.blurple()
        )

        embed1.add_field(
            name="📋 Prerequisites",
            value=(
                "• Python **3.12+**\n"
                "```bash\npython --version\n```\n"
                "• Git\n"
                "• FFmpeg (for music features)"
            ),
            inline=False
        )

        embed2 = discord.Embed(
            title="⚙️ Installation",
            color=discord.Color.green()
        )

        embed2.add_field(
            name="1️⃣ Clone Repository",
            value=(
                "```bash\n"
                "git clone https://github.com/Mohit-Mano06/TaskForge-Bot.git\n"
                "cd TaskForge-Bot\n"
                "```"
            ),
            inline=False
        )

        embed2.add_field(
            name="2️⃣ Setup Environment",
            value=(
                "**Recommended: Using `uv`**\n"
                "```bash\n"
                "uv init\n"
                "uv sync\n"
                "```\n"
                "**Alternative: Standard Python**\n"
                "```bash\n"
                "python -m venv venv\n"
                ".\\venv\\Scripts\\activate\n"
                "pip install -r requirements.txt\n"
                "```"
            ),
            inline=False
        )

        embed3 = discord.Embed(
            title="🚀 Run the Bot",
            color=discord.Color.orange()
        )

        embed3.add_field(
            name="Run Bot",
            value=(
                "**With `uv`:**\n"
                "```bash\nuv run python main.py\n```\n"
                "**Standard:**\n"
                "```bash\npython main.py\n```"
            ),
            inline=False
        )

        embed3.add_field(
            name="Environment Variable",
            value=(
                "Create a `.env` file:\n"
                "```env\nDISCORD_TOKEN=your_bot_token_here\n```"
            ),
            inline=False
        )

        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)


async def setup(bot):
    await bot.add_cog(SetupGuide(bot))