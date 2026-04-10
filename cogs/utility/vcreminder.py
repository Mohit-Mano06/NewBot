import discord 
from discord.ext import commands
import json
import os 
import time
from database import load_reminders, save_reminders
from .reminder import parse_time

REMINDER_FILE = "data/reminder.json"

class VCReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Set a voice channel reminder")
    async def vcreminder(self, ctx, time_input: str, *, message: str):
        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel to set a VC reminder!")
            return

        seconds = parse_time(time_input)
        if seconds is None:
            await ctx.send("❌ Invalid Time Format. Use '10m', '2h', '4d'.")
            return
        
        trigger_time = int(time.time()) + seconds
        data = await load_reminders()
        new_id = len(data["reminders"]) + 1

        reminder = {
            "id": new_id,
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "voice_channel_id": ctx.author.voice.channel.id,
            "message": message,
            "trigger_time": trigger_time,
            "status": "pending",
            "type": "voice"
        }

        data["reminders"].append(reminder)
        await save_reminders(data)
        await ctx.send(f"⏰ VC Reminder set for `{time_input}` in {ctx.author.voice.channel.name}: **{message}**")



async def setup(bot):
    await bot.add_cog(VCReminder(bot))
