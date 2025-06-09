import discord
from discord.ext import commands
from discord import app_commands, InteractionType, InteractionResponse
import config
from datetime import datetime

from managers.roles_manager import BotRolesManager


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_manager: BotRolesManager = bot.roles_manager

    @app_commands.command(name="add_member", description="Add a member as part of Legion")
    @BotRolesManager.require_role("Senator")
    async def add_member(self, interaction: discord.Interaction, user: discord.Member):
        data = await self.bot.db.new_user(user.id, user.joined_at.timestamp(), datetime.now().timestamp())
        output = f"Name: {interaction.guild.get_member(data[0]).display_name} - Join Date: <t:{int(data[1])}> - Member Date: <t:{int(data[2])}>"
        await interaction.response.send_message(output, ephemeral=True)

    @app_commands.command(name="remove_member", description="Remove a member as part of Legion")
    @BotRolesManager.require_role("Senator")
    async def remove_member(self, interaction: discord.Interaction, user: discord.Member):
        data = await self.bot.db.remove_user(user.id)
        output = f"Name: {interaction.guild.get_member(data[0]).display_name} - Join Date: <t:{int(data[1])}> - Member Date: <t:{int(data[2])}>"
        await interaction.response.send_message(output, ephemeral=True)

    @app_commands.command(name="get_member", description="Get user data")
    @BotRolesManager.require_role("Senator")
    async def get_member(self, interaction: discord.Interaction, user: discord.Member):
        data = await self.bot.db.remove_user(user.id)
        output = f"Name: {interaction.guild.get_member(data[0]).display_name} - Join Date: <t:{int(data[1])}> - Member Date: <t:{int(data[2])}>"
        await interaction.response.send_message(output, ephemeral=True)

    @app_commands.command(name="synccmd")
    @commands.has_permissions(administrator=True)
    async def synccmd(self, interaction: discord.Interaction):
        fmt = await self.bot.tree.sync(guild=interaction.guild_id)
        await interaction.response.send_message(
            f"Synced {len(fmt)} commands to the current server",
            ephemeral=True
        )

    @app_commands.command(name="globalsync")
    @commands.has_permissions(administrator=True)
    async def globalsync(self, interaction: discord.Interaction):
        fmt = await self.bot.tree.sync()
        await interaction.response.send_message(
            f"Synced {len(fmt)} commands globally",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
