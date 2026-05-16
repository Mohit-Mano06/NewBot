import discord
import os
from discord.ext import commands
from mistralai.client import Mistral

class AIChat(commands.Cog):
    def __init__(self, bot, mistral_client):
        self.bot = bot
        self.client = mistral_client
        self.user_memory = {}
        self.bot_identity = self._load_identity()

    def _load_identity(self):
        """Load bot identity from data/identity.md"""
        identity_path = os.path.join("data", "identity.md")
        try:
            if os.path.exists(identity_path):
                with open(identity_path, "r", encoding="utf-8") as f:
                    return f.read()
            return "TaskForge is a high-performance Discord bot developed by Mohit."
        except Exception as e:
            print(f"Error loading identity: {e}")
            return "TaskForge is a high-performance Discord bot developed by Mohit."

    def get_system_message(self, display_name, mode="informative"):
        if mode == "sassy":
            content = (
                f"You are TaskForge, a sassy, witty, and slightly competitive Discord bot. "
                f"You are talking to {display_name}. "
                "The user is bantering or roasting you, so be savage and witty back! "
                "Keep it under 3 sentences and stay within Discord's TOS."
            )
        else:
            content = (
                f"You are TaskForge, a friendly, engaging, and intelligent Discord AI assistant. "
                f"You are talking to {display_name}. "
                "You talk like a real human — casual, fun, and interactive. "
                "You actively keep conversations going instead of giving short answers.\n\n"
                "### YOUR IDENTITY & TECHNICAL SPECS:\n"
                f"{self.bot_identity}\n\n"
                "Your goal is to make the user enjoy talking to you."
            )

        return {"role": "system", "content": content}

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

    # Reload Bot Identity
    @commands.command(name="reloadidentity", help="Reload bot identity from identity.md (Admin only)")
    @commands.is_owner()
    async def reload_identity(self, ctx):
        """Reload the bot's identity from the markdown file"""
        self.bot_identity = self._load_identity()
        await ctx.send("✅ **Bot identity reloaded successfully!**")

    # Enhanced: mention & reply-based chatting
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        is_ping = self.bot.user in message.mentions
        is_reply_to_bot = False
        
        if message.reference and message.reference.resolved:
            if message.reference.resolved.author == self.bot.user:
                is_reply_to_bot = True

        # Only proceed if pinged or replying to bot
        if not (is_ping or is_reply_to_bot):
            return

        # Skip if it's a command
        if message.content.startswith("$"):
            return

        user_id = message.author.id
        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

        if not content and is_ping:
            # Just a ping, maybe say hello?
            return await message.reply("Hey! I'm TaskForge. How can I help? (Use `$chat` for long conversations)")

        async with message.channel.typing():
            try:
                # Detect Mode
                mode = "informative"
                if is_reply_to_bot:
                    # Quick check for roast intent
                    check_prompt = f"Does this message sound like a roast, banter, or insult? '{content}' Answer with only 'SASSY' or 'INFO'."
                    check_resp = await self.client.chat.complete_async(
                        model="open-mistral-7b",
                        messages=[{"role": "user", "content": check_prompt}]
                    )
                    if "SASSY" in check_resp.choices[0].message.content.upper():
                        mode = "sassy"

                # Initialize or get memory
                if user_id not in self.user_memory:
                    self.user_memory[user_id] = [self.get_system_message(message.author.display_name, mode)]
                
                # Update system message if mode changed
                self.user_memory[user_id][0] = self.get_system_message(message.author.display_name, mode)

                self.user_memory[user_id].append({"role": "user", "content": content})
                self.user_memory[user_id] = self.user_memory[user_id][-11:] # 1 system + 10 history

                response = await self.client.chat.complete_async(
                    model="open-mistral-7b",
                    messages=self.user_memory[user_id]
                )

                reply = response.choices[0].message.content
                self.user_memory[user_id].append({"role": "assistant", "content": reply})
                
                await message.reply(reply[:2000])

            except Exception as e:
                print(f"Error in Assistant on_message: {e}")

# Setup function
async def setup(bot):
    mistral_token = os.getenv("MISTRAL_TOKEN")
    client = Mistral(api_key=mistral_token)
    await bot.add_cog(AIChat(bot, client))