import discord
from discord.ext import commands
import asyncio

import config


class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if "ticket" in channel.name.lower():
            await asyncio.sleep(5)
            await channel.send("""
                               Hello! Welcome to the Legion Discord Server! Please answer these questions to help us get this started!
            1) Have you read and agree to the ⁠rules?
            2) Are you over 18?
            3) Are you planning on joining the Legion, are a member of one of its Allies, or are just here to Visit?
            4) What is your username in Bitcraft?
            5) Are you currently a member of any other group?
            6) What is your primary (and secondary if applicable) language?
            7) What made you interested in joining The Legion? Were you invited by anyone?
    
                               """)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(30)
        await member.send("""
            Hello! Thank you for joining the discord server for The Legion, our group for Bitcraft Online.
            Please make sure you head to this message in the welcome channel and click the button to create a ticket.
            This will allow you to access the rest of the server.
            https://discordapp.com/channels/1267584422253694996/1317666800896577638/1317673462495711322
            """)
        print(f"Pinged {member.name} with join info")

    @discord.app_commands.command(name="count_professions", description="Display a count of member professions", guild=config.GUILD_ID)
    async def count_professions(self, interaction: discord.Interaction):
        await interaction.response.send_message("Getting profession counts", ephemeral=True)
        output = '```'
        role_count = 0

        guild = interaction.guild

        for role_name, role_id in config.PROFESSION_ROLES.items():
            # TODO modify the role count and output to include character limits
            role_count += 1

            role = guild.get_role(role_id)
            member_role = guild.get_role(config.GUILD_MEMBER_ID)

            members_with_role = []

            for member in role.members:
                if member_role in member.roles:
                    members_with_role.append(member)

            output += f"{role_name.title():14} -"
            if members_with_role:
                # this combines all the names of the members with the role into one string separated by commas the same as before
                output += " " + ", ".join(members_with_role)
            output += f" - ({len(members_with_role)})\n\n"

            if role_count % 4 == 0:
                output += "```"
                await interaction.followup.send(output)
                output = "```"

            elif role_count == len(config.PROFESSION_ROLES):
                output += "```"
                await interaction.followup.send(output)

        return

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))