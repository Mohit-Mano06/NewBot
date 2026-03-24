from discord.ext import commands
import discord
import math

class HelpView(discord.ui.View):
    def __init__(self, bot, cog_commands, ctx):
        super().__init__(timeout=60)
        self.bot = bot
        self.cog_commands = cog_commands
        self.ctx = ctx
        self.current_cog = None
        self.page = 0
        self.per_page = 5

        # Add category buttons
        for cog_name in cog_commands:
            self.add_item(CategoryButton(cog_name, self))

    def get_page_content(self):
        commands_list = self.cog_commands[self.current_cog]
        total_pages = math.ceil(len(commands_list) / self.per_page)

        start = self.page * self.per_page
        end = start + self.per_page

        page_commands = commands_list[start:end]

        text = f"**📂 {self.current_cog} Commands (Page {self.page+1}/{total_pages})**\n\n"
        text += "\n".join(f"`{self.ctx.prefix}{cmd}`" for cmd in page_commands)

        return text, total_pages


class CategoryButton(discord.ui.Button):
    def __init__(self, cog_name, view):
        super().__init__(label=cog_name, style=discord.ButtonStyle.primary)
        self.cog_name = cog_name
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        view = self.view_ref
        view.current_cog = self.cog_name
        view.page = 0

        content, _ = view.get_page_content()
        await interaction.response.edit_message(content=content, view=view)


class NextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="➡️", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        view = self.view_ref
        _, total_pages = view.get_page_content()

        if view.page + 1 < total_pages:
            view.page += 1

        content, _ = view.get_page_content()
        await interaction.response.edit_message(content=content, view=view)


class PrevButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⬅️", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        view = self.view_ref

        if view.page > 0:
            view.page -= 1

        content, _ = view.get_page_content()
        await interaction.response.edit_message(content=content, view=view)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        cog_commands = {}

        for command in self.bot.commands:
            if command.hidden:
                continue

            cog_name = command.cog.qualified_name if command.cog else "General"

            if cog_name not in cog_commands:
                cog_commands[cog_name] = []

            cog_commands[cog_name].append(command.name)

        # sort commands
        for cog in cog_commands:
            cog_commands[cog].sort()

        view = HelpView(self.bot, cog_commands, ctx)

        # add pagination buttons AFTER selecting category
        view.add_item(PrevButton(view))
        view.add_item(NextButton(view))

        await ctx.send(
            "**📜 Select a category below:**",
            view=view
        )


async def setup(bot):
    await bot.add_cog(Help(bot))