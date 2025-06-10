from functools import wraps

import discord
from discord import Interaction, app_commands


class BotRolesManager:
    def __init__(self, config, bot):
        self.roles_config = config.ROLES
        self.bot: discord.Client = bot

    def get_role_info(self, role_key: str):
        role_info = self.roles_config.get(role_key)
        if role_info:
            return role_info

        # if direct key lookup fails, try to find by matching role name (case-insensitive, contains)
        search_key_lower = role_key.lower()
        for key, info in self.roles_config.items():
            configured_names = info.get("name") or info.get("names")
            if configured_names is None:
                continue

            if isinstance(configured_names, str):
                configured_names_list = [configured_names]
            elif isinstance(configured_names, list):
                configured_names_list = configured_names
            else:
                continue

            for conf_name in configured_names_list:
                if search_key_lower in str(conf_name).lower():
                    return info

        return None

    def get_role_id(self, role_key: str):
        role_info = self.get_role_info(role_key)
        if role_info:
            return role_info.get("id") or role_info.get("ids")
        return None

    def get_role_name(self, role_key: str):
        role_info = self.get_role_info(role_key)
        if role_info:
            return role_info.get("name") or role_info.get("names")
        return None

    def get_guild_id(self):
        return self.roles_config.get("GUILD").get("id")

    def get_guild_object(self):
        guild: discord.Guild = self.bot.get_guild(self.get_guild_id())
        return guild

    def get_guild_members(self):
        guild = self.get_guild_object()
        if guild:
            return guild.members
        return []

    def get_role_by_id(self, role_id: int):
        guild = self.get_guild_object()
        if guild:
            return guild.get_role(role_id)
        return None

    def get_role_by_name(self, role_name: str):
        guild = self.get_guild_object()
        role_id = self.get_role_id(role_name)
        if guild:
            for role in guild.roles:
                if role.id == role_id or role_name.lower() in role.name.lower():
                    return role
        return None

    def get_members_by_role(self, role_name: str, ignore_bots=True):
        role = self.get_role_by_name(role_name)
        if not role:
            return []
        if ignore_bots:
            return [member for member in role.members if not member.bot]
        return role.members

    def get_verified_members(self):
        """Get all members with the 'Legionnaire' role."""
        return self.get_members_by_role("Legionnaire", ignore_bots=True)

    @staticmethod
    def require_role(role_name: str):
        """LegionBot custom Decorator that restricts Discord command access to users with a specific role.

            Usage:
                @BotRolesManager.require_role("Legionnaire")
                async def some_command(self, interaction: Interaction):
                    # Only users with the "Legionnaire" role can execute this
                    ...

            Args:
                role_name: The name or key of the required role as defined in the role config

            Raises:
                MissingRole: If the user lacks the required role
                AppCommandError: If role configuration is invalid or missing
            """
        def decorator(func):
            @wraps(func)
            async def wrapped(self, interaction: Interaction, *args, **kwargs):
                roles_manager = getattr(interaction.client, 'roles_manager', None)
                if not roles_manager:
                    raise app_commands.AppCommandError("Bot configuration error: roles manager not found")

                role_info = roles_manager.get_role_info(role_name)
                if not role_info:
                    raise app_commands.AppCommandError(f"Role '{role_name}' not found in configuration")

                user_roles = getattr(interaction.user, 'roles', [])
                if not any(role.id == int(role_info['id']) for role in user_roles):
                    raise app_commands.MissingRole(role_info.get('name', role_name))

                return await func(self, interaction, *args, **kwargs)
            return wrapped
        return decorator



