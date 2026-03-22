from discord.ext import commands

class LinkedInTranslator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.mistral_client  # IMPORTANT

    @commands.command(name="linkedin")
    async def linkedin(self, ctx, *, text: str):
        """Convert casual text into LinkedIn-style post"""

        prompt = f"""
You are a LinkedIn content expert who transforms simple, casual sentences into professional, engaging LinkedIn-style posts.

Rules:
- Expand the input into a short LinkedIn post (4–8 lines max)
- Use a professional, slightly dramatic tone
- Add gratitude, reflection, or "journey" elements
- Include corporate buzzwords (growth, opportunity, learning, journey, etc.)
- Keep it slightly humorous but still believable
- Avoid emojis unless they fit naturally (max 2)
- Do NOT repeat the original sentence verbatim

Input: "{text}"
Output:
"""

        try:
            async with ctx.typing():
                response = await self.client.chat.complete_async(
                    model="mistral-large-latest",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )

            output = response.choices[0].message.content.strip()

            if len(output) > 1900:
                output = output[:1900] + "..."

            await ctx.send(f"💼 **LinkedIn Version:**\n\n{output}")

        except Exception as e:
            await ctx.send(f"❌ Error: `{str(e)}`")

    @linkedin.error
    async def linkedin_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide text.\nExample: `$linkedin I got promoted`")


async def setup(bot):
    await bot.add_cog(LinkedInTranslator(bot))