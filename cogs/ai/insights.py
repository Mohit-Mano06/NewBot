import discord
from discord.ext import commands, tasks
from collections import defaultdict, deque


class ExplainView(discord.ui.View):
    def __init__(self, cog, topic, current_level, author_id):
        super().__init__(timeout=180)
        self.cog = cog
        self.topic = topic
        self.current_level = str(current_level)
        self.author_id = author_id

        levels = ["1", "5", "10", "engineer"]
        self.next_level = None
        if self.current_level in levels:
            idx = levels.index(self.current_level)
            if idx < len(levels) - 1:
                self.next_level = levels[idx + 1]

        if self.next_level:
            button = discord.ui.Button(label=f"Next Level ({self.next_level})", style=discord.ButtonStyle.primary, emoji="⏭️")
            button.callback = self.next_callback
            self.add_item(button)

    async def next_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("Only the person who asked can request the next level!", ephemeral=True)
        
        await interaction.response.defer()
        
        # Disable the button on the current message
        self.clear_items()
        await interaction.edit_original_response(view=self)

        # Send the next level
        await self.cog.send_explanation(interaction.channel, self.next_level, self.topic, self.author_id)


class AIInsights(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.client = bot.mistral_client
        self.message_history = defaultdict(lambda: deque(maxlen=200))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        self.message_history[message.guild.id].append(message.content)

    async def send_explanation(self, channel, level, topic, author_id):
        # Concise prompt to reduce latency and token count
        prompt = f"""
        Explain the topic "{topic}" strictly for an audience level of "{level}".
        
        Guidelines:
        - level 1: Simple words and analogies (ELI5).
        - level 5: Simple, clear general overview.
        - level 10: Academic/Detailed.
        - level engineer: Technical, architectural, implementation focus.

        RULES:
        1. ONLY explain for level "{level}".
        2. Keep it under 250 words and 1500 characters.
        3. Use bullet points for readability.
        4. Be direct—no conversational filler.
        """

        try:
            status_msg = await channel.send("⚡ **Generating AI Insight...**")
            async with channel.typing():
                response = await self.client.chat.complete_async(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4, # Lower temperature for more direct, reliable explanations
                    max_tokens=800
                )
            
            await status_msg.delete()
            output = response.choices[0].message.content.strip()
            
            # Smart message splitting for Discord's 2000-char limit
            # We split by 1900 to leave room for headers/styling
            parts = [output[i:i + 1900] for i in range(0, len(output), 1900)]
            
            view = ExplainView(self, topic, level, author_id)
            
            # Send the first part with the view (buttons)
            await channel.send(f"🧠 **Insight (Level {level}) | {topic}:**\n\n{parts[0]}", view=view if len(parts) == 1 else None)
            
            # Send remaining parts if any
            if len(parts) > 1:
                for i in range(1, len(parts)):
                    is_last = (i == len(parts) - 1)
                    await channel.send(parts[i], view=view if is_last else None)
        
        except Exception as e:
            await channel.send(f"❌ Error generating explanation: `{str(e)}`")

    @commands.command(name="explain", help="AI explanation of a topic at a given level (1, 5, 10, engineer)")
    async def explain(self, ctx, level:str, *, topic:str):
        await self.send_explanation(ctx.channel, level, topic, ctx.author.id)
    
    @explain.error
    async def explain_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ Usage:\n"
                "`$explain (level 1 or 5 or 10 or engineer) topic`\n"
                "*Example: `$explain 5 black holes`*"
            )

    @commands.command(name="obsessions", help="Analyze recent chat trends for server interests")
    async def obsessions(self, ctx):
        messages = list(self.message_history[ctx.guild.id])
        if not messages: 
            return await ctx.send("❌ Not enough chat data yet to analyze trends.")
        
        # Analyze last 150 messages for context
        context_text = "\n".join(messages[-150:])
        prompt = f"""
        Identify 3-5 trending server topics from these messages:
        {context_text}
        
        Rules: Concise topics (1-3 words). 
        Format:
        🔥 Server Obsessions:
        • Topic 1
        • Topic 2
        """
        try:
            async with ctx.typing():
                response = await self.client.chat.complete_async(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
            await ctx.send(response.choices[0].message.content.strip())
        except Exception as e:
            await ctx.send(f"❌ Analysis failed: `{str(e)}`")

async def setup(bot):
    await bot.add_cog(AIInsights(bot))
    


        