import discord
from discord.ext import commands
import datetime
import asyncio
import sys
import os
from logger import send_log

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file")
except ImportError:
    print("dotenv library not found. Ensure it is installed.")

TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_TOKEN")

# Diagnostic logging
print(f"Token retrieved: {'Yes' if TOKEN else 'No'}")
print(f"Mistral Token retrieved: {'Yes' if MISTRAL_API_KEY else 'No'}")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found! Check your .env file or environment variables")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
print("Intents configured.")

ALLOWED_CHANNEL_ID = 1469612261827022949

class TaskForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="$",
            intents=intents,
            help_command=None
        )

    async def close(self):
        print("Shutting down bot...")
        channel = self.get_channel(ALLOWED_CHANNEL_ID)
        if channel:
            try:
                async for message in channel.history(limit=10):
                    if message.author == bot.user and "Bot is offline" in message.content:
                        await message.delete()
                await channel.send("🔴 **Bot is offline**")
            except Exception as e:
                print(f"Error sending shutdown message: {e}")
        
        try:
            await send_log(self, "🔴 **Bot is offline** (Log Channel Message)")
        except Exception as e:
            print(f"Error sending shutdown log: {e}")

        await super().close()

bot = TaskForgeBot()

@bot.event
async def on_ready():
    # Only run this once to avoid rate limits on reconnection
    if hasattr(bot, 'init_done'):
        print(f"Bot reconnected: {bot.user}")
        return

    bot.init_done = True
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.datetime.now(datetime.timezone.utc)
    
    print(f"Logged in as {bot.user} (Initial Setup)")

    channel = bot.get_channel(ALLOWED_CHANNEL_ID)
    if channel:
        try:
            async for message in channel.history(limit=10):
                if message.author == bot.user and "Bot is online" in message.content:
                    await message.delete()

            await channel.send("🟢 **Bot is online**")
        except Exception as e:
            print(f"Warning: Could not send startup message: {e}")

    try:
        await send_log(bot, "🟢 **Bot is online** (Log Channel Message)")
    except Exception as e:
        print(f"Warning: Could not send log message: {e}")

@bot.event
async def setup_hook():
    print("Starting setup_hook (loading extensions)...")
    extensions = [
        "cogs.general.utility", "cogs.general.info", "cogs.reminder.reminder",
        "cogs.reminder.vcreminder", "cogs.music.music_player", "cogs.admin.moderation",
        "cogs.general.confession", "cogs.general.announcement", "cogs.general.setupguide",
        "cogs.mistral.ai_dj", "cogs.mistral.ai_chat", "cogs.system", "cogs.mistral.bot_chat.chat", "cogs.general.status"
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded {ext}")
        except Exception as e:
            print(f"❌ Failed to load {ext}: {e}")
    print("setup_hook complete.")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Bot Help",
        description="List of available commands grouped by category",
        color=0x3498db
    )
    cog_commands = {}
    for command in bot.commands:
        if command.hidden:
            continue
        cog_name = command.cog.qualified_name if command.cog else "General"
        if cog_name not in cog_commands:
            cog_commands[cog_name] = []
        cog_commands[cog_name].append(f"`{command.name}`")

    for cog_name, commands_list in cog_commands.items():
        embed.add_field(name=cog_name, value=", ".join(commands_list), inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)
    raise error

@bot.command(name="sync", hidden=True)
@commands.is_owner()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands.")
    except Exception as e:
        await ctx.send(f"Error syncing: {e}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Command is on cooldown. Try again in {error.retry_after:.2f}s", ephemeral=True)
    elif isinstance(error, discord.app_commands.CheckFailure):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        print(f"Interaction error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

## ==== STARTUP ==== ##
from keep_alive import keep_alive
keep_alive()

print("Waiting 3 seconds for system to settle...")
import time
time.sleep(3)

print("Attempting to start bot.run()...")
try:
    bot.run(TOKEN)
except KeyboardInterrupt:
    print("\n[!] Manual shutdown detected.")
except Exception as e:
    print(f"FATAL ERROR during bot.run(): {e}")
    if "1015" in str(e):
        print("💡 TIP: You are being rate limited by Cloudflare/Discord. Try restarting the Render service or changing the region.")
