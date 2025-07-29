import discord
from discord import app_commands
from discord.ext import commands
from utils import BaseCog
from collections import defaultdict

class HelpPaginator(discord.ui.View):
    def __init__(self, commands_by_cog: dict[str, list[app_commands.Command]], interaction: discord.Interaction, base_cog: BaseCog, commands_per_page=5):
        super().__init__(timeout=120)
        self.commands_by_cog = commands_by_cog
        self.pages = []
        self.current_page = 0
        self.interaction = interaction
        self.base_cog = base_cog
        self.commands_per_page = commands_per_page
        self.message = None

        self.command_id_map = {}

    async def setup(self):
        try:
            if self.interaction.guild:
                registered_commands = await self.base_cog.bot.tree.fetch_commands(guild=self.interaction.guild)
            else:
                registered_commands = await self.base_cog.bot.tree.fetch_commands()
            self.command_id_map = {cmd.name: cmd.id for cmd in registered_commands}
        except Exception:
            self.command_id_map = {}

        self._generate_pages()
        self.populate_select_options()
        self._update_buttons()

    def _generate_pages(self):
        all_entries = []

        for cog_name, cmds in self.commands_by_cog.items():
            cmd_lines = []
            for cmd in cmds:
                cmd_id = self.command_id_map.get(cmd.name)
                command_display = f"</{cmd.name}:{cmd_id}>" if cmd_id else f"/{cmd.name}"
                cmd_lines.append(f"{command_display} — {cmd.description or 'No description'}")
            all_entries.append((cog_name, cmd_lines))

        self.pages.clear()
        current_page = discord.Embed(
            title="Help",
            color=discord.Color.blue()
        )
        current_count = 0

        for cog_name, cmd_lines in all_entries:
            if current_count + len(cmd_lines) > self.commands_per_page and current_count > 0:
                self.pages.append(current_page)
                current_page = discord.Embed(
                    title="Help",
                    color=discord.Color.blue()
                )
                current_count = 0

            value = "\n".join(cmd_lines)
            current_page.add_field(name=cog_name, value=value, inline=False)
            current_count += len(cmd_lines)

        if len(current_page.fields) > 0:
            self.pages.append(current_page)

        total_pages = len(self.pages)
        for i, embed in enumerate(self.pages):
            embed.description = f"Page {i+1} of {total_pages} (click a command to autofill)"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.interaction.user

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)

    async def send_initial_message(self):
        await self.interaction.response.send_message(embed=self.pages[0], view=self, ephemeral=True)
        self.message = await self.interaction.original_response()

    def _update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= len(self.pages) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.select(
        placeholder="Select a command to copy usage",
        options=[],
        min_values=1,
        max_values=1,
        row=1
    )
    async def command_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        cmd_name = select.values[0]
        for cmds in self.commands_by_cog.values():
            for cmd in cmds:
                if cmd.name == cmd_name:
                    usage = f"/{cmd.name}"
                    await interaction.response.send_message(
                        f"Command usage: `{usage}`\nYou can copy and paste it to use.",
                        ephemeral=True
                    )
                    return
        await interaction.response.send_message("Command not found.", ephemeral=True)

    def populate_select_options(self):
        options = []
        for cog_name, cmds in self.commands_by_cog.items():
            for cmd in cmds:
                options.append(discord.SelectOption(
                    label=cmd.name,
                    description=f"{cog_name}: {cmd.description or 'No description'}",
                    value=cmd.name
                ))
        self.command_select.options = options


class Help(BaseCog):
    COG_LABEL = "Info"

    @app_commands.command(name="help", description="Show help with all commands")
    async def help(self, interaction: discord.Interaction):
        commands_by_cog = defaultdict(list)

        for cog in self.bot.cogs.values():
            if not hasattr(cog, "walk_app_commands"):
                continue

            cmds = []
            for cmd in cog.walk_app_commands():
                if not isinstance(cmd, app_commands.Command):
                    continue
                if not await self.can_run(cmd, interaction):
                    continue
                cmds.append(cmd)

            if cmds:
                cog_name = getattr(cog, "COG_LABEL", cog.__class__.__name__)
                commands_by_cog[cog_name].extend(cmds)

        if not commands_by_cog:
            await self.reply_defer_checked(interaction=interaction, content="No commands available.", ephemeral=True)
            return

        paginator = HelpPaginator(commands_by_cog, interaction, self)
        await paginator.setup()
        await paginator.send_initial_message()

setup = Help.setup
