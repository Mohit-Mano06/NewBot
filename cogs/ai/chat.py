# pyrefly: ignore [missing-import]
import discord
import os
import asyncio
import re
from discord.ext import commands
from mistralai.client import Mistral

class BotChat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mistral = Mistral(api_key=os.getenv("MISTRAL_TOKEN"))

    @commands.command(help="Chat with TaskForge using AI")
    async def chat(self, ctx, *, message: str):
        """Chat with TaskForge using AI"""
        async with ctx.typing():
            try:
                history = [
                    {"role": "system", "content": "You are TaskForge, a witty, productive, and slightly competitive Discord bot. Give short, funny, and slightly sassy replies. Keep it under 3 sentences."},
                    {"role": "user", "content": message}
                ]
                response = await self.mistral.chat.complete_async(
                    model="mistral-small-latest",
                    messages=history
                )
                reply = response.choices[0].message.content
                await ctx.reply(reply)
            except Exception as e:
                await ctx.send("I'm a bit overwhelmed right now. Try again later!")
                print(f"Error in chat command: {e}")

    @commands.command(help="Roast someone or yourself!")
    async def roast(self, ctx, *, input_text: str = None):
        """Roast someone or yourself!"""
        # If the command is triggered, we start typing immediately to show responsiveness
        async with ctx.typing():
            try:
                # 1. Determine the target
                target_mention = ctx.author.mention
                raw_context = input_text if input_text else ""
                
                # Check for mentions in the message
                if ctx.message.mentions:
                    # Get the first person mentioned that isn't the bot
                    mentioned_users = [u for u in ctx.message.mentions if u != self.bot.user]
                    
                    if not mentioned_users and self.bot.user in ctx.message.mentions:
                        # User only mentioned the bot
                        target_mention = ctx.author.mention
                        raw_context = "trying to roast the bot"
                    elif mentioned_users:
                        # Roast the first mentioned user
                        target_mention = mentioned_users[0].mention
                        # Clean up the context by removing all mentions
                        raw_context = re.sub(r'<@!?[0-9]+>', '', raw_context).strip()
                
                final_context = raw_context if raw_context else "their overall vibe"

                # 2. Build the prompt
                prompt = f"""
                You are TaskForge, a savage and brutal Discord bot. 
                Your goal is to deliver a world-class roast to {target_mention} based on this context: "{final_context}".
                Be creative, mean (but funny), and stay within Discord's TOS. 
                Keep it concise (1-2 sentences).
                Do NOT include the target's name or mention in your reply; I will handle that.
                """

                # 3. Call the AI
                response = await self.mistral.chat.complete_async(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": prompt}]
                )
                roast_content = response.choices[0].message.content
                
                # 4. Send the result with an actual ping
                await ctx.send(f"{target_mention}, {roast_content}")

            except Exception as e:
                print(f"Roast Command Error: {e}")
                # Try to give some feedback
                if "1015" in str(e) or "rate limit" in str(e).lower():
                    await ctx.send("I'm being rate-limited. Even I need a break from roasting you losers.")
                else:
                    await ctx.send("I tried to roast you, but the AI cringed so hard it crashed. Try again.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Simple prefix check
        prefix = "$"
        if self.bot.user.mentioned_in(message) and not message.content.startswith(prefix):
            async with message.channel.typing():
                try:
                    prompt = f"Roast {message.author.mention} brutally in 1-2 sentences for pinging you. Do not mention them in your reply."
                    response = await self.mistral.chat.complete_async(
                        model="mistral-small-latest",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    await message.reply(f"{message.author.mention}, {response.choices[0].message.content}")
                except Exception as e:
                    print(f"Auto-roast error: {e}")

async def setup(bot):
    await bot.add_cog(BotChat(bot))