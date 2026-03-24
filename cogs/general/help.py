import discord
from discord.ext import commands
import math

class HelpSelect(discord.ui.Select):
    def __init__(self, bot, cog_commands, ctx):
        options = []
        
        # Category Mapping with Emojis
        self.category_styles = {
            "Admin": "🛠️",
            "AI Assistant": "🤖",
            "Music": "🎵",
            "Utility": "⚙️",
            "Social": "📢",
            "Info": "📁",
            "General": "📦"
        }

        for cog_name in cog_commands:
            emoji = self.category_styles.get(cog_name, "🔹")
            options.append(discord.SelectOption(
                label=cog_name,
                description=f"View {cog_name} commands",
                emoji=emoji
            ))

        super().__init__(placeholder="📂 Select a category...", min_values=1, max_values=1, options=options)
        self.bot = bot
        self.cog_commands = cog_commands
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        commands_list = self.cog_commands[cog_name]
        
        # Sort commands
        commands_list.sort()
        
        emoji = self.category_styles.get(cog_name, "🔹")
        
        text = f"### {emoji} {cog_name} Commands\n\n"
        
        for cmd_name in commands_list:
            cmd = self.bot.get_command(cmd_name)
            desc = cmd.help if cmd and cmd.help else "No description available."
            text += f"🔹 **{self.ctx.prefix}{cmd_name}**\n   └ *{desc}*\n"

        text += f"\n*Use `{self.ctx.prefix}help <command>` for more details on a specific command.*"
        
        await interaction.response.edit_message(content=text, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, bot, cog_commands, ctx):
        super().__init__(timeout=60)
        self.add_item(HelpSelect(bot, cog_commands, ctx))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, *, command_name: str = None):
        """Shows help for a category or command"""
        
        if command_name:
            # Search for specific command help
            cmd = self.bot.get_command(command_name)
            if not cmd:
                return await ctx.send(f"❌ Command `{command_name}` not found.")
            
            help_text = f"### 🔍 Help: {ctx.prefix}{cmd.name}\n"
            help_text += f"> **Description:** {cmd.help or 'No description'}\n"
            if cmd.aliases:
                help_text += f"> **Aliases:** {', '.join(cmd.aliases)}\n"
            usage = cmd.usage or f"{ctx.prefix}{cmd.name} {cmd.signature}"
            help_text += f"> **Usage:** `{usage}`\n"
            
            return await ctx.send(help_text)

        # Mapping Cogs to categories
        cog_mapping = {
            "Moderation": "Admin",
            "MusicPlayer": "Music",
            "Utility": "Utility",
            "Reminder": "Utility",
            "VCReminder": "Utility",
            "AIChat": "AI Assistant",
            "Insights": "AI Assistant",
            "Chat": "AI Assistant",
            "AIDJ": "Music",
            "Confession": "Social",
            "Info": "Info",
            "Status": "Info",
            "General": "General"
        }

        cog_commands = {}

        for command in self.bot.commands:
            if command.hidden:
                continue

            cog_name = command.cog.qualified_name if command.cog else "General"
            category = cog_mapping.get(cog_name, cog_name)

            if category not in cog_commands:
                cog_commands[category] = []

            cog_commands[category].append(command.name)

        view = HelpView(self.bot, cog_commands, ctx)

        welcome_text = (
            "## 📜 TaskForge Help Menu\n"
            "Welcome to the TaskForge help menu! Use the dropdown below to explore our features.\n\n"
            "🛠️ **Admin** - Commands for moderators\n"
            "🤖 **AI Assistant** - Talk to TaskForge AI\n"
            "🎵 **Music** - Play tunes and manage queues\n"
            "⚙️ **Utility** - Reminders and helpful tools\n"
            "📢 **Social** - Confessions and fun\n"
            "📁 **Info** - Bot information and status"
        )

        await ctx.send(welcome_text, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))

# ==========================================
# PREVIOUS HELP COMMAND STRUCTURE (FALLBACK)
# ==========================================
"""
class PreviousHelpView(discord.ui.View):
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
"""