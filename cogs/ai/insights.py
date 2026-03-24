from discord.ext import commands, tasks
from collections import defaultdict, deque


class AIInsights(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.client = bot.mistral_client

        self.message_history = defaultdict(lambda: deque(maxlen=200))

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        self.message_history[message.guild.id].append(message.content)


    @commands.command(name="explain", help="AI explanation of a topic at a given level (1, 5, 10, engineer)")
    async def explain(self, ctx, level:str, *, topic:str):
        prompt = f"""
        You are an expert teacher.
        Explain the topic "{topic}" 
        Audience level : {level}

        Rules: 
        - 1 → explain like a child
        - 5 → simple and clear 
        - 10 → detailed and technical
        - engineer → technical and detailed
        - Use examples where useful 
        - Keep it structured and easy to understand
        """

        try: 
            async with ctx.typing():
                response = self.client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6
                )
            
            output = response.choices[0].message.content.strip()

            if len(output) > 1900:
                output = output[:1900] + "..."
            
            await ctx.send(f"🧠 **Explanation ({level})**:\n\n{output}")
        
        except Exception as e:
            await ctx.send(f"❌ Error: `{str(e)}`")
    
    @explain.error
    async def explain_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ Usage:\n"
                "`$explain 5 black holes`\n"
                "`$explain 15 APIs`\n"
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

            Messages:
            {combined_text}

            Rules:
            - Extract 3 to 5 topics
            - Each topic should be 1–3 words
            - Focus on repeated or important themes
            - Ignore spam

            Format:
            🔥 Server Obsessions:
            • Topic 1
            • Topic 2
            • Topic 3
        """

        try:
            async with ctx.typing():
                response = self.client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
            
            output = response.choices[0].message.content.strip()
            await ctx.send(output)

        except Exception as e:
            await ctx.send(f"❌ Error: `{str(e)}`")


async def setup(bot):
    await bot.add_cog(AIInsights(bot))
    


        