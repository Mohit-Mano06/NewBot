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
        prompt = f"""
        You are an expert teacher.
        Explain the topic "{topic}" strictly for an audience level of "{level}".
        
        Strict Level Guidelines:
        - level 1: Explain like I'm 5 years old. Use very simple words and analogies.
        - level 5: Simple and clear explanation for a general audience.
        - level 10: Detailed and academic explanation.
        - level engineer: Highly technical, focusing on implementation details and architecture.

        IMPORTANT: ONLY provide the explanation for level "{level}". Do NOT include headers or content for other levels.
        Keep it structured and easy to understand.
        """

        try:
            status_msg = await channel.send("✨ **AI Magic in progress... Analyzing your topic...**")
            async with channel.typing():
                response = await self.client.chat.complete_async(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6
                )
            
            await status_msg.delete()
            output = response.choices[0].message.content.strip()
            if len(output) > 1900:
                output = output[:1900] + "..."
            
            view = ExplainView(self, topic, level, author_id)
            await channel.send(f"🧠 **Explanation (Level {level}) for {topic}:**\n\n{output}", view=view)
        
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
                "`$explain (level 1[beginner] or 5[intermediate] or 10[advanced] or engineer[expert]) question/topic`\n"
                "`$explain 5 black holes`\n"
                "`$explain 10 APIs`\n"
                "`$explain engineer OAuth`"
            )

    @commands.command(name="obsessions", help="Analyze recent chat trends to see what the server is obsessed with")
    async def obsessions(self, ctx):
        messages = list(self.message_history[ctx.guild.id])
        if not messages: 
            await ctx.send("❌ Not enough data yet.")
            return
        
        combined_text = "\n".join(messages[-150:])
        prompt = f"""
        Analyze the following chat messages and identify trending topics.
        Messages: {combined_text}
        Rules: Extract 3 to 5 topics (1-3 words each).
        Format:
        🔥 Server Obsessions:
        • Topic 1
        • Topic 2
        """
        try:
            async with ctx.typing():
                response = await self.client.chat.complete_async(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
            await ctx.send(response.choices[0].message.content.strip())
        except Exception as e:
            await ctx.send(f"❌ Error: `{str(e)}`")

async def setup(bot):
    await bot.add_cog(AIInsights(bot))
    


        