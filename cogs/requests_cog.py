# cogs/requests_cog.py
import discord
from discord.ext import commands
from discord import app_commands


class RequestsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="request_list", description="Get a list of open requests")
    async def request_list(self, interaction: discord.Interaction):
        await interaction.response.send_message("Fetching Requests...", ephemeral=True)
        output = "```"
        # I love camel case too T-T
        name_padding = 0
        request_padding = 0
        claimant_padding = 0

        # Access the database instance from the bot
        requests_data = await self.bot.db.get_requests(interaction.guild.id)

        if not requests_data:
            await interaction.followup.send("No open requests found.", ephemeral=True)
            return

        # TODO Calculate dynamic padding for better formatting
        for req in requests_data:
            claim_name = interaction.guild.get_member(req.claimant_id).display_name if req.claimant_id else "Unclaimed"
            user_name = interaction.guild.get_member(req.requestor_id).display_name
            resource = req.resource[0:40]
            name_padding = max(name_padding, len(user_name))
            request_padding = max(request_padding, len(resource))
            claimant_padding = max(claimant_padding, len(claim_name))


        name_padding += 4
        request_padding += 4
        claimant_padding += 4

        count = 0
        for req in requests_data:
            claim_name = interaction.guild.get_member(req.claimant_id).display_name if req.claimant_id else "Unclaimed"

            if len(req.resource) > 40:
                resource = req.resource[0:40]
                resource += "..."
            else:
                resource = req.resource

            user_name = interaction.guild.get_member(req.requestor_id).display_name
            output += f"\n {user_name: <{name_padding}} - {resource: <{request_padding}} - {claim_name: <{claimant_padding}} - {req.id}"
            count += 1

            # TODO change discord character limit handling
            if count % 10 == 0:
                output += "```"
                await interaction.followup.send(output)
                output = "```"
            elif count == len(requests_data):
                output += "```"
                await interaction.followup.send(output)

    @app_commands.command(name="request", description="Request a resource")
    async def request(self, interaction: discord.Interaction, resource: str):
        request_id = await self.bot.db.insert_request(interaction.guild.id, interaction.user.id, resource)
        await interaction.response.send_message(f"""
        Requester: {interaction.user.mention}
        Resource: {resource}
        Request ID: `{request_id}`
        """, ephemeral=True)

    @app_commands.command(name="claim", description="Claim a resource request")
    async def claim(self, interaction: discord.Interaction,
                    request_id: int):  # Renamed 'id' to 'request_id' for clarity

        current_request = await self.bot.db.claim_request(request_id, interaction.guild.id, interaction.user.id)

        if current_request is None:
            await interaction.response.send_message("That ID didn't work, please double check it!",
                                                    ephemeral=True)
            return

        await interaction.response.send_message(f"""
            <@{current_request.requestor_id}>
                Claimant: {interaction.user.display_name.capitalize()}
                Resource: {current_request.resource}
                Request ID: {request_id}
            """)

    @app_commands.command(name="unclaim", description="Unclaim a request")
    async def unclaim(self, interaction: discord.Interaction, request_id: int):
        current_request = await self.bot.db.unclaim_request(request_id, interaction.guild.id, interaction.user.id)

        if current_request is None:
            await interaction.response.send_message(
                "That Request ID didn't work, please double check it!",
                ephemeral=True)
            return

        await interaction.response.send_message(
            f"You have successfully unclaimed {current_request.resource}(Request ID: `{request_id}`).", ephemeral=True)

    @app_commands.command(name="complete", description="Complete a request")
    async def complete(self, interaction: discord.Interaction, request_id: int):
        current_request = await self.bot.db.finish_request(request_id, interaction.guild.id, interaction.user.id)

        if current_request is None:
            await interaction.response.send_message("That ID didn't work, please double check it!",
                                                        ephemeral = True)
            return

        await interaction.response.send_message(f"""
            <@{current_request.requestor_id}>
                Completer: {interaction.user.display_name.capitalize()}
                Resource: {current_request.resource}
                Request ID: {request_id}
            """)

    @app_commands.command(name="claims", description="See which requests you've claimed")
    async def claims(self, interaction: discord.Interaction):
        claimed_requests = await self.bot.db.get_claims(interaction.guild.id, interaction.user.id)
        output = ''

        if not claimed_requests:
            await interaction.response.send_message("You haven't claimed any requests.", ephemeral=True)
            return

        output += f"{interaction.user.display_name}'s Claimed Requests:\n"
        for req in claimed_requests:
            requestor_name = interaction.guild.get_member(req.requestor_id).display_name
            output += f" - `{req.id}`: {req.resource} (Requested by: {requestor_name.capitalize()})\n"
        await interaction.response.send_message(output, ephemeral=True)

    @app_commands.command(name="requests", description="See a list of requests you've made")
    async def requests(self, interaction: discord.Interaction):
        user_requests = await self.bot.db.get_user_requests(interaction.guild.id, interaction.user.id)
        output = ''

        if not user_requests:
            await interaction.response.send_message("You haven't made any requests.", ephemeral=True)
            return

        output += f"Your Requests:\n"
        for req in user_requests:
            status = "Claimed" if req.claimant_id else "Unclaimed"
            claimant_info = f" by {interaction.guild.get_member(req.claimant_id).display_name}" if req.claimant_id else ""
            output += f" - `{req.id}`: {req.resource} ({status}{claimant_info})\n"
        await interaction.response.send_message(output, ephemeral=True)


# Required function to load the cog
async def setup(bot):
    await bot.add_cog(RequestsCog(bot))