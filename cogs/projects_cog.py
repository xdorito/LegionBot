# cogs/projects_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import time # For time.time()


class ProjectsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="new_project", description="Create a new project")
    async def new_project(self, interaction: discord.Interaction, name: str):
        project_id = await self.bot.db.new_project(interaction.guild.id, name, time.time())

        if project_id is None:
            await interaction.response.send_message("Something went wrong and your project didn't get made. Contact Lanidae so they can contact xDorito", ephemeral=True)
        else:
            await interaction.response.send_message(f"Your project has been created! Your project's name is {name} and its id is {project_id}", ephemeral=False)

    @app_commands.command(name="add_resource", description="Add a resource to the project")
    async def add_resource(self, interaction: discord.Interaction, resource: str, amount: int, project_id: int):
        success = await self.bot.db.add_resource(resource, amount, project_id, interaction.guild.id)
        if success:
            await interaction.response.send_message(f"You have added {amount} - {resource} to project: `{project_id}`.")

    @app_commands.command(name="remove_resource", description="Remove a resource from a project")
    async def remove_resource(self, interaction: discord.Interaction, resource: str, project_id: int):
        success = await self.bot.db.remove_resource(resource, project_id, interaction.guild.id)
        if success:
            await interaction.response.send_message(f"You have removed {resource} from Project: `{project_id}`.")

    @app_commands.command(name="list_projects", description="Display a list of active projects")
    async def list_projects(self, interaction: discord.Interaction):
        await interaction.response.send_message("Fetching Project List...", ephemeral=True)
        project_data = await self.bot.db.list_projects(interaction.guild.id)
        output = "```"
        count = 0

        if not project_data:
            await interaction.followup.send("No active projects found.", ephemeral=True)
            return

        for project in project_data:
            output += f"\n {project[0].title()} - {project[1]}"
            count += 1
            if count % 20 == 0:
                output += "```"
                await interaction.followup.send(output)
                output = "```"
            elif count == len(project_data):
                output += "```"
                await interaction.followup.send(output)

    @app_commands.command(name="get_contributors", description="Get a list of people who have contributed to this project")
    async def get_contributors(self, interaction: discord.Interaction, project_id: int):
        await interaction.response.send_message("Fetching Contributors...", ephemeral=True)
        contributor_data = await self.bot.list_contributors(project_id, interaction.guild_id)
        output = "```"
        count = 0
        for contributor in contributor_data:
            output += f"\n{interaction.guild.get_member(contributor[0]).display_name}"
            count += 1
            if count % 20 == 0:
                output += "```"
                await interaction.followup.send(output)
                output = "```"
            elif count == len(contributor_data):
                output += "```"
                await interaction.followup.send(output)

    @app_commands.command(name="get_contributions", description="Get a list of what resources members have been contributed to this project")
    async def get_contributions(self, interaction: discord.Interaction, project_id: int):
        await interaction.response.send_message("Fetching Contributions...", ephemeral=True)
        contributions_data = await self.bot.list_contributions(project_id, interaction.guild_id)
        output = "```"
        count = 0
        lastid = None
        for contribution in contributions_data:
            if lastid != contribution[0] or count % 20 == 0:
                lastid = contribution[0]
                output += f"\n{interaction.guild.get_member(contribution[0]).display_name}"
                count += 1
            output += f"\n\t{contribution[1]} - {contribution[2]}"
            count += 1
            if count % 20 == 0:
                output += "```"
                await interaction.followup.send(output)
                output = "```"
            elif count >= len(contributions_data):
                output += "```"
                await interaction.followup.send(output)

    @app_commands.command(name="get_resources", description="Get a list of what resources are in this project")
    async def get_resources(self, interaction: discord.Interaction, project_id: int):
        await interaction.response.send_message("Fetching Resources...", ephemeral=True)
        resources_data = await self.bot.list_resources(project_id, interaction.guild_id)
        output = "```"
        count = 0
        for resource in resources_data:
            output += f"\n{resource[0] : <16} - {resource[1] : >7} / {resource[2] : >7}"
            count += 1
            if count % 20 == 0:
                output += "```"
                await interaction.followup.send(output)
                output = "```"
            elif count == len(resources_data):
                output += "```"
                await interaction.followup.send(output)

    @app_commands.command(name="contribute", description="Record your contributions to a project")
    async def contribute(self, interaction: discord.Interaction, project_id: int, resource: str, amount: int):
        await self.bot.db.contribute_resources(project_id, resource, amount, interaction.user.id, interaction.guild_id)
        await interaction.response.send_message(
            f"Thank you for your contribution! You contributed {amount} - {resource} to project: {project_id}",
            ephemeral=True)

    @app_commands.command(name="finish_project", description="Finish a project, good job!")
    async def finish_project(self, interaction: discord.Interaction, project_id: int):
        name = await self.bot.db.complete_project(project_id, interaction.guild_id)
        await interaction.response.send_message(f"You've marked project {name} - {project_id} as complete!")


# Required function to load the cog
async def setup(bot):
    await bot.add_cog(ProjectsCog(bot))
