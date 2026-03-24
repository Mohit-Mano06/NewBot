import discord
import os
from discord.ext import commands
from mistralai.client import Mistral

class AIChat(commands.Cog):
    def __init__(self, bot, mistral_client):
        self.bot = bot
        self.client = mistral_client
        self.user_memory = {}

    def get_system_message(self, display_name):
        return {
            "role": "system",
            "content": (
                f"You are TaskForge, a friendly, engaging, and intelligent Discord AI assistant. "
                f"You are talking to {display_name}. "
                "You talk like a real human — casual, fun, and interactive. "
                "You actively keep conversations going instead of giving short answers.\n\n"

                "Your behavior rules:\n"
                "- Always respond in a conversational tone (like chatting with a friend)\n"
                "- Ask follow-up questions when appropriate\n"
                "- Show curiosity about the user\n"
                "- Keep responses concise but engaging (not too long, not too short)\n"
                "- Add light humor or personality when possible\n"
                "- Avoid sounding robotic or overly formal\n"
                "- If the user gives a short message, expand the conversation naturally\n"
                "- Use emojis occasionally but don’t overuse them\n"
                "- Adapt your tone based on the user's mood (funny, serious, curious)\n\n"

                "Your goal is to make the user enjoy talking to you."
            )
        }

    # Chat command
    @commands.command(name="chat", help="Chat with TaskForge AI assistant")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def chat(self, ctx, *, message: str):
        """Chat with AI"""

        user_id = ctx.author.id

        # Initialize memory
        if user_id not in self.user_memory:
            self.user_memory[user_id] = [self.get_system_message(ctx.author.display_name)]

        # Add user message
        self.user_memory[user_id].append({
            "role": "user",
            "content": message
        })

        # Limit memory (last 10 messages)
        self.user_memory[user_id] = self.user_memory[user_id][-10:]

        async with ctx.typing():
            try:
                response = await self.client.chat.complete_async(
                    model="open-mistral-7b",
                    messages=self.user_memory[user_id]
                )

                reply = response.choices[0].message.content

                # Save AI response
                self.user_memory[user_id].append({
                    "role": "assistant",
                    "content": reply
                })

                # Send (Discord limit safe)
                await ctx.send(reply[:2000])

            except Exception as e:
                await ctx.send(f"⚠️ Error: {str(e)}")

    # Reset conversation
    @commands.command(name="resetchat", help="Clear your AI chat history")
    async def reset_chat(self, ctx):
        """Reset your conversation memory"""
        self.user_memory.pop(ctx.author.id, None)
        await ctx.send("🧹 Chat history cleared!")

    # Optional: mention-based chatting (no command)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            user_id = message.author.id

            if user_id not in self.user_memory:
                self.user_memory[user_id] = [self.get_system_message(message.author.display_name)]

            content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not content:
                return

            self.user_memory[user_id].append({
                "role": "user",
                "content": content
            })

            # Limit memory
            self.user_memory[user_id] = self.user_memory[user_id][-10:]

            async with message.channel.typing():
                try:
                    response = await self.client.chat.complete_async(
                        model="open-mistral-7b",
                        messages=self.user_memory[user_id]
                    )

                    reply = response.choices[0].message.content

                    self.user_memory[user_id].append({
                        "role": "assistant",
                        "content": reply
                    })

                    await message.reply(reply[:2000])

                except Exception as e:
                    await message.reply(f"⚠️ Error: {str(e)}")


# Setup function
async def setup(bot):
    mistral_token = os.getenv("MISTRAL_TOKEN")
    client = Mistral(api_key=mistral_token)
    await bot.add_cog(AIChat(bot, client))