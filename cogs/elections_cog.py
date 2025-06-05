# cogs/election_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import pickle
import os
from datetime import datetime, timedelta

import config
import utils
from utils import load_state, save_state
import candidate as candidate_model

CANDIDATES_PICKLE = "candidates.p"

class ElectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Access shared state and candidate list from bot instance
        self.state = load_state()


        # candidate type

        self.candidates = self._load_candidates()

    @staticmethod
    def _load_candidates():
        try:
            candidates_list = pickle.load(open(CANDIDATES_PICKLE, "rb"))
            return candidates_list
        except FileNotFoundError:
            return []

    def _save_candidates(self):
        try:
            pickle.dump(self.candidates, open(CANDIDATES_PICKLE, "wb"))
        except Exception as e:
            print(f"Error saving {CANDIDATES_PICKLE}: {e}")


    @app_commands.command(name="candidate", description="Declare yourself as a candidate for Senate.")
    @app_commands.checks.has_role(config.GUILD_MEMBER_ID)  # Using constant for member role
    async def candidate(self, interaction: discord.Interaction):
        # Check for ongoing election
        if not self.state['ELECTION_STARTED']:
            await interaction.response.send_message(
                "There's no election running right now. Please wait for an election to declare your candidacy.",
                ephemeral=True)
            return

        # Check for disciplinary marks
        member = interaction.guild.get_member(interaction.user.id)
        for role_id in config.DISCIPLINARY_ROLES:
            if interaction.guild.get_role(role_id) in member.roles:
                await interaction.response.send_message(
                    "Sorry, you have a disciplinary mark. Only members in good standing can be Senators.",
                    ephemeral=True)
                return

        # Check user join date
        user_data = await self.bot.db.get_user(interaction.user.id)
        if user_data is None:
            await interaction.response.send_message(
                "You are not registered as a Legion member in our database. Please ensure you've been added.",
                ephemeral=True)
            return

        member_date = datetime.fromtimestamp(user_data[2])  # user_data[2] is member_date_timestamp
        time_since_member = discord.utils.utcnow() - member_date.replace(
            tzinfo=None)  # Ensure datetime objects are naive or timezone-aware consistently

        if time_since_member < timedelta(days=30):
            await interaction.response.send_message(
                f"You haven't been a Legion member long enough! You need to have been in the guild for at least one month ({30 - time_since_member.days} days remaining) to be a Senator!",
                ephemeral=True)
            return

        # Check if new candidate declarations are allowed
        if not self.state['CANDIDATES_ALLOWED']:
            await interaction.response.send_message(
                "Sorry, the period to declare your candidacy has ended. You'll have to try again next election.",
                ephemeral=True)
            return

        # Check if user is already a candidate
        for c in self.candidates:
            if c.name == interaction.user.name:
                await interaction.response.send_message(
                    "It looks like you're already a candidate, no need to put yourself in twice!", ephemeral=True)
                return

        # Assign new candidate ID
        candidate_id = max(x.cid for x in self.candidates) + 1

        new_candidate = candidate_model.Candidate(interaction.user.display_name, interaction.user.id, candidate_id)
        self.candidates.append(new_candidate)
        self._save_candidates()  # Save changes to pickle

        await interaction.response.send_message(f"""
        Thank you for submitting your candidacy for the Legion Senate!
        Name: {new_candidate.name}
        **Candidate ID:** `{new_candidate.cid}`
        """)

    @app_commands.command(name="start_election", description="Start an election!")
    @app_commands.checks.has_role(config.ADMINISTRATOR_ROLE)  # Only administrators can start elections
    async def start_election(self, interaction: discord.Interaction):
        """Starts a new Senate election, allowing candidates to declare."""
        if self.state['ELECTION_STARTED']:
            await interaction.response.send_message("An election is already in progress!", ephemeral=True)
            return

        self.state['ELECTION_STARTED'] = True
        self.state['CANDIDATES_ALLOWED'] = True
        self._save_state()

        # Clear previous candidates and votes for a new election
        self.candidates = []
        self._save_candidates()

        await interaction.response.send_message(
            "A new Legion Senate election has started! Candidates can now declare themselves.", ephemeral=False)

    @app_commands.command(name="start_voting", description="Stop candidate declarations and start voting.")
    @app_commands.checks.has_role(config.ADMINISTRATOR_ROLE)
    async def start_voting(self, interaction: discord.Interaction):
        if not self.state['ELECTION_STARTED']:
            await interaction.response.send_message("No election is currently active to start voting.", ephemeral=True)
            return
        if not self.state['CANDIDATES_ALLOWED']:
            await interaction.response.send_message(
                "Candidate declarations have already ended. Voting is likely already in progress.", ephemeral=True)
            return
        self.state['CANDIDATES_ALLOWED'] = False
        self._save_state()

        await interaction.response.send_message(
            "Candidate declarations have closed. Voting for the Senate election can now begin!", ephemeral=False)

    @app_commands.command(name="withdraw", description="Withdraw yourself as a candidate")
    @app_commands.checks.has_role(config.GUILD_MEMBER_ID)
    async def withdraw(self, interaction: discord.Interaction):
        original_candidate_count = len(self.candidates)
        self.candidates = [c for c in self.candidates if c.uid != interaction.member.id]

        if len(self.candidates) < original_candidate_count:
            self._save_candidates()
            await interaction.response.send_message("You have successfully withdrawn yourself as a candidate.",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("You were not found in the list of candidates.", ephemeral=True)

    @app_commands.command(name="vote", description="Vote for a candidate!")
    @app_commands.checks.has_role(config.GUILD_MEMBER_ID)
    async def vote(self, interaction: discord.Interaction, candidate_id: int):  # Renamed 'cid' for clarity
        if self.state['CANDIDATES_ALLOWED']:
            await interaction.response.send_message(
                "Voting has not started yet. Please wait for the voting phase to begin.", ephemeral=True)
            return
        if not self.state['ELECTION_STARTED']:
            await interaction.response.send_message("No election is currently active.", ephemeral=True)
            return

        voter_id = interaction.user.id

        for c in self.candidates:
            if c.cid == candidate_id:
                c.Vote(voter_id, c.cid)
                await interaction.response.send_message(f"Thank you for voting for {c.name}", ephemeral=True)
                self._save_candidates()
                return
        else:
            await interaction.response.send_message("Invalid Candidate ID. Please check the list of candidates.",
                                                    ephemeral=True)

    @app_commands.command(name="remove_vote", description="Remove your vote for a candidate")
    @app_commands.checks.has_role(config.GUILD_MEMBER_ID)
    async def remove_vote(self, interaction: discord.Interaction, candidate_id: int):
        if self.state['CANDIDATES_ALLOWED']:
            await interaction.response.send_message("Voting has not started yet.", ephemeral=True)
            return
        if not self.state['ELECTION_STARTED']:
            await interaction.response.send_message("No election is currently active.", ephemeral=True)
            return

        voter_id = interaction.user.id
        for c in self.candidates:
            if c.cid == candidate_id:
                c.RemoveVote(voter_id)
                await interaction.response.send_message(
                    f"You have successfully removed your vote for {c.name}.", ephemeral=True)
                self._save_candidates()
                return

    @app_commands.command(name="list_candidates", description="List all candidates for the election")
    @app_commands.checks.has_role(config.GUILD_MEMBER_ID)
    async def list_candidates(self, interaction: discord.Interaction):
        if not self.state['ELECTION_STARTED']:
            await interaction.response.send_message(
                "No election is currently active, so there are no candidates to list.", ephemeral=True)
            return

        if not self.candidates:
            await interaction.response.send_message("No candidates have declared yet for this election.",
                                                    ephemeral=True)
            return

        output = ""
        for c in self.candidates:
            output += f'{c.name} - {c.cid}\n'
        await interaction.response.send_message(output, ephemeral=True)

    @app_commands.command(name="end_election", description="End a senate election")
    @app_commands.checks.has_role(config.ADMINISTRATOR_ROLE)
    async def end_election(self, interaction: discord.Interaction, senator_count: int):
        if not self.state['ELECTION_STARTED']:
            await interaction.response.send_message("No election is currently active to end.", ephemeral=True)
            return

        self.state['ELECTION_STARTED'] = False
        self.state['CANDIDATES_ALLOWED'] = False  # Ensure this is also false
        utils.save_state(self.state)

        # Sort candidates by votes in descending order
        sorted_candidates = sorted(self.candidates, key=lambda x: x.votes, reverse=True)

        output = "**Legion Senate Election Results:**\n\n"
        output += "--------------------------------------\n"
        output += "Top Candidates (New Senators):\n"
        output += "--------------------------------------\n"

        senate_role = interaction.guild.get_role(config.SENATOR_ROLE)
        administrator_role = interaction.guild.get_role(config.ADMINISTRATOR_ROLE)

        # Remove Senator/Administrator roles from ALL members first, for a clean slate
        # TODO better way to do this?
        await interaction.response.send_message("Ending election and resetting Senator roles...", ephemeral=True)
        for member in interaction.guild.members:
            if senate_role and senate_role in member.roles:
                try:
                    await member.remove_roles(senate_role, reason="Election prep: Resetting Senator roles.")
                except discord.Forbidden:
                    print(f"Error: Bot lacks permissions to remove Senator role from {member.display_name}.")
                except Exception as e:
                    print(f"Error removing Senator role from {member.display_name}: {e}")
            if administrator_role and administrator_role in member.roles:  # Assuming Admins might also be Senators for some reason
                try:
                    await member.remove_roles(administrator_role,
                                              reason="Election prep: Resetting Admin roles if previously Senator.")
                except discord.Forbidden:
                    print(f"Error: Bot lacks permissions to remove Admin role from {member.display_name}.")
                except Exception as e:
                    print(f"Error removing Admin role from {member.display_name}: {e}")

        # Assign Senator roles to the top `senator_count` candidates
        new_senators_count = 0
        for i, candidate in enumerate(sorted_candidates):
            if new_senators_count < senator_count:
                member = interaction.guild.get_member(candidate.uid)
                if member and senate_role:
                    try:
                        await member.add_roles(senate_role, reason="Won Legion Senate Election.")
                        output += f'**{candidate.name}** (Votes: {candidate.votes}) - **NEW SENATOR**\n'
                        new_senators_count += 1
                    except discord.Forbidden:
                        output += f'{candidate.name} (Votes: {candidate.votes}) - **ERROR: Cannot assign Senator role (permissions)**\n'
                        print(f"Error: Bot lacks permissions to assign Senator role to {member.display_name}.")
                    except Exception as e:
                        output += f'{candidate.name} (Votes: {candidate.votes}) - **ERROR: {e}**\n'
                        print(f"Error assigning Senator role to {member.display_name}: {e}")
                elif not member:
                    output += f'{candidate.name} (Votes: {candidate.votes}) - **User not found in guild**\n'
            else:
                # List remaining candidates, just for visibility
                output += f'{candidate.name} (Votes: {candidate.votes})\n'

        output += "\n--------------------------------------\n"
        output += "**Full Election Rankings (All Candidates):**\n"
        output += "--------------------------------------\n"
        for candidate in sorted_candidates:
            output += f'- {candidate.name}: {candidate.votes} votes (ID: `{candidate.cid}`)\n'

        await interaction.followup.send(output, ephemeral=False)  # Send results publicly

        # Clean up pickle file after election
        try:
            if os.path.exists(CANDIDATES_PICKLE):
                os.remove(CANDIDATES_PICKLE)
                print(f"Removed {CANDIDATES_PICKLE} after election.")
            self.candidates = []  # Clear internal list
        except Exception as e:
            print(f"Error deleting {CANDIDATES_PICKLE}: {e}")


# Required function to load the cog
async def setup(bot):
    await bot.add_cog(ElectionCog(bot))