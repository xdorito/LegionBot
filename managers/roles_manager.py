from functools import wraps
from discord import Interaction, app_commands

class BotRolesManager:
    def __init__(self, config):
        self.roles_config = config.ROLES


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
                    # Found a match, return the role info
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



