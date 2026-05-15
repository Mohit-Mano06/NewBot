# TaskForge-Bot - Developed by Mohit
# GitHub: https://github.com/Mohit-Mano06/TaskForge-Bot
# License: MIT

import discord
from discord.ext import commands
import datetime
import asyncio
import sys
import os
import traceback
from logger import send_log
from mistralai.client import Mistral
import database
from bot_logger import log_print, RICH_ENABLED, rich_terminal

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    log_print("Loaded .env file")
except ImportError:
    log_print("dotenv library not found. Ensure it is installed.", "warning")

TOKEN = os.getenv("TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_TOKEN")

# Diagnostic logging
log_print(f"Token retrieved: {'Yes' if TOKEN else 'No'}")
log_print(f"Mistral Token retrieved: {'Yes' if MISTRAL_API_KEY else 'No'}")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found! Check your .env file or environment variables")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
log_print("Intents configured.")

ALLOWED_CHANNEL_ID = 1469612261827022949

class TaskForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="$",
            intents=intents,
            help_command=None
        )
        self.mistral_client = Mistral(api_key=MISTRAL_API_KEY)

    async def close(self):
        log_print("Shutting down bot...")
        channel = self.get_channel(ALLOWED_CHANNEL_ID)
        if channel:
            try:
                async for message in channel.history(limit=10):
                    if message.author == self.user and "Bot is offline" in message.content:
                        await message.delete()
                await channel.send("🔴 **Bot is offline**")
            except Exception as e:
                log_print(f"Error sending shutdown message: {e}", "error")
        
        try:
            await send_log(self, "🔴 **Bot is offline** (Log Channel Message)")
        except Exception as e:
            log_print(f"Error sending shutdown log: {e}", "error")

        await super().close()

bot = TaskForgeBot()

@bot.event
async def on_ready():
    # Only run this once to avoid rate limits on reconnection
    if hasattr(bot, 'init_done'):
        log_print(f"Bot reconnected: {bot.user}")
        return
    
    bot.init_done = True
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.datetime.now(datetime.timezone.utc)
    
    log_print(f"Logged in as {bot.user} (Initial Setup)", "success")

    channel = bot.get_channel(ALLOWED_CHANNEL_ID)
    if channel:
        try:
            async for message in channel.history(limit=10):
                if message.author == bot.user and "Bot is online" in message.content:
                    await message.delete()

            await channel.send("🟢 **Bot is online**")
        except Exception as e:
            log_print(f"Warning: Could not send startup message: {e}", "warning")

    try:
        await send_log(bot, "🟢 **Bot is online** (Log Channel Message)")
    except Exception as e:
        log_print(f"Warning: Could not send log message: {e}", "warning")
        
    if database.USE_SUPABASE:
        try:
            connected = await database.check_supabase_connection()
            if connected:
                log_print("✅ Supabase REST API connected", "success")
            else:
                log_print("❌ Supabase REST API failed to connect", "error")
        except Exception as e:
            log_print(f"❌ Supabase error: {e}", "error")

@bot.event
async def setup_hook():
    extensions = [
        "cogs.utility.tools", "cogs.general.help", "cogs.general.info", "cogs.utility.reminder",
        "cogs.utility.vcreminder", "cogs.music.player", "cogs.admin.moderation",
        "cogs.social.confession", "cogs.general.announcement", "cogs.general.guide",
        "cogs.music.dj", "cogs.ai.assistant", "cogs.ai.insights", "cogs.system", "cogs.ai.chat", "cogs.general.status",
        "cogs.economy.economy",
        "cogs.economy.shop",
        "cogs.leaderboard.leaderboard_tracker",
        "cogs.leaderboard.leaderboard_commands"
    ]
    
    if RICH_ENABLED:
        await rich_terminal.load_extensions_with_ui(bot, extensions)
    else:
        print("Starting setup_hook (loading extensions)...")
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"✅ Loaded {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}: {e}")
        print("setup_hook complete.")


#### ====== Deprecated Help Command ====== ####
""""@bot.command(name="help")
async def help_command(ctx):
    cog_commands = {}

    for command in bot.commands:
        if command.hidden:
            continue

        cog_name = command.cog.qualified_name if command.cog else "General"

        if cog_name not in cog_commands:
            cog_commands[cog_name] = []

        cog_commands[cog_name].append(command.name)

    message = "**📜 Available Commands**\n\n"

    for cog_name, commands_list in cog_commands.items():
        message += f"**{cog_name}**\n"
        message += " | ".join(f"`{cmd}`" for cmd in commands_list)
        message += "\n\n"

    await ctx.send(message)
    """

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return
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
        log_print(f"Interaction error: {error}", "error")
        if not interaction.response.is_done():
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)


log_print("Waiting 3 seconds for system to settle...")
import time
time.sleep(3)

log_print("Attempting to start bot.run()...")
try:
    bot.run(TOKEN)
except KeyboardInterrupt:
    log_print("\n[!] Manual shutdown detected.", "warning")
except Exception as e:
    log_print(f"FATAL ERROR during bot.run(): {e}", "error")
    if "1015" in str(e):
        log_print("💡 TIP: You are being rate limited by Cloudflare/Discord. Try restarting the Render service or changing the region.", "warning")
