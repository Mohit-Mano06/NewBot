from discord.ext import commands

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        @commands.command(help = "Greets you")
        async def hello(ctx):
            print("hello command received")  # Debug
            await ctx.send("Hello 👋")
        
        @commands.command(help = "Shows info about you")
        async def me(ctx):
            user = ctx.author


            msg = (
                f"Username: {user.name}\n"
                f"ID: {user.id}\n"
                f"Joined at: {user.joined_at}\n"
                f"Avatar URL: {user.display_avatar.url}\n"
            )

            await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(Social(bot))