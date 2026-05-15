# pyrefly: ignore [missing-import]
import discord
import os
import asyncio
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
        # Default target is the author
        target_mention = ctx.author.mention
        context = input_text if input_text else "their existence"
        
        # Check if someone was mentioned in the command
        if ctx.message.mentions:
            mentioned_user = ctx.message.mentions[0]
            
            # If they mentioned the bot itself, roast the author
            if mentioned_user == self.bot.user:
                target_mention = ctx.author.mention
                context = "the audacity to try and roast me"
            else:
                # Roast the mentioned user
                target_mention = mentioned_user.mention
                # Remove the mention from the context string
                context = input_text.replace(mentioned_user.mention, "").strip()
                if not context:
                    context = "their existence"

        prompt = f"""
        You are TaskForge, a savage, and brutal Discord bot. 
        Your goal is to deliver a world-class roast to {target_mention} based on this context: "{context}".
        Be creative, mean (but funny), and stay within Discord's TOS. 
        Keep it concise (under 1-2 sentences).
        Don't use generic roasts; make it personal to the context if provided.
        """

        async with ctx.typing():
            try:
                response = await self.mistral.chat.complete_async(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": prompt}]
                )
                roast = response.choices[0].message.content
                await ctx.send(roast)
            except Exception as e:
                await ctx.send("I'm too tired to roast you right now... check back later.")
                print(f"Error in roast command: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from itself or other bots
        if message.author.bot:
            return

        # Check if someone pinged the bot directly (without a command)
        if self.bot.user.mentioned_in(message) and not message.content.startswith(tuple(await self.bot.get_prefix(message))):
            async with message.channel.typing():
                prompt = f"""
                You are TaskForge, a savage and brutal Discord bot. 
                {message.author.mention} just had the audacity to ping you. 
                Roast them into oblivion in 1-2 sentences. 
                Make it funny but devastating.
                """
                try:
                    response = await self.mistral.chat.complete_async(
                        model="mistral-small-latest",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    roast = response.choices[0].message.content
                    await message.reply(roast)
                except Exception as e:
                    print(f"Error in auto-roast: {e}")

async def setup(bot):
    await bot.add_cog(BotChat(bot))