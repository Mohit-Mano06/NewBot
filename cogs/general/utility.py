import random
import datetime
import time
import discord
from discord.ext import commands

class Utility (commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(help = "Roll a dice")
    async def roll(self,ctx):
        await ctx.send(f"You rolled {random.randint(1,6)} 🎲")

    @commands.command(help="Tells your ping and runtime")
    async def ping(self, ctx): #Measure API ping-time
        start_time = time.monotonic()
        message = await ctx.send("🏓 Pinging...")
        api_latency = (time.monotonic() - start_time) * 1000
        websocket_latency = self.bot.latency * 1000

        if websocket_latency > 250:
            msg = "Just switch to 2g atp 😭"
        elif websocket_latency > 200: 
            msg = "You have shit ping 💀"
        elif websocket_latency < 100:
            msg = "Bro lives in the Wifi Router ⚡"
        else: 
            msg = "Ping is good stop whining"

        await message.edit(content=f"**API Latency:** {api_latency:.2f}ms\n**WebSocket Latency:** {websocket_latency:.2f}ms\n{msg}")

    @commands.command(help = "Greets you")
    async def hello(self,ctx):
        await ctx.send("Hello 👋")

    @commands.command(help="List members in your current voice channel")
    async def vcmembers(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("❌ You must be in a voice channel!")
            
        vc_channel = ctx.author.voice.channel
        members = [member.display_name for member in vc_channel.members if not member.bot]
        
        if members:
            member_list = "\n".join(members)
            await ctx.send(f"👥 Members in {vc_channel.name}:\n{member_list}")
        else:
            await ctx.send(f"🔇 No members in {vc_channel.name}")

    @commands.command(help="Show voice channel connection and stats")
    async def vcstat(self, ctx):
        status_lines = []
        
        websocket_ping = self.bot.latency * 1000
        ping_status = "🟢 Low" if websocket_ping < 150 else ("🟡 Medium" if websocket_ping < 250 else "🔴 High")
            
        status_lines.append(f"📡 WebSocket Ping: {websocket_ping:.2f}ms ({ping_status})")
        
        if ctx.guild.voice_client:
            vc = ctx.guild.voice_client
            channel = vc.channel
            member_count = len([m for m in channel.members if not m.bot])
            status_lines.append(f"🔊 Connected to: {channel.name}")
            status_lines.append(f"👥 Members: {member_count}")
        else:
            status_lines.append("🔇 Not currently in a voice channel")
        
        await ctx.send("\n".join(status_lines))

async def setup(bot):
    # Initialize start_time with timezone-aware datetime
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.datetime.now(datetime.timezone.utc)
    await bot.add_cog(Utility(bot))
