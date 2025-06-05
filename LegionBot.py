import pickle
import random
from datetime import datetime


import database_sqlite
import candidate as cand
import config
import utils as util

import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(config.BOT_PREFIX, intents=intents)
bot.config = config

def load_pickle_files():
    global project_list
    global votes
    global candidates
    try:
        project_list = pickle.load(open("project_list.p", "rb"))
    except FileNotFoundError:
        project_list = []

    try:
        votes = pickle.load(open("votes.p", "rb"))
    except FileNotFoundError:
        votes = []

    try:
        candidates = pickle.load(open("candidates.p", "rb"))
    except FileNotFoundError:
        candidates = []
    return

db = database_sqlite.DatabaseSqlite()
db.setup_db()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    # TODO load cogs

    #ping_metronome.start()

@tasks.loop(minutes=67)
async def legion_advert():
    if int(datetime.now().timestamp()) - STATE['LAST_ANNOUNCE'] < 57600:
        return
    # STATE['LAST_ANNOUNCE'] = int(datetime.now().timestamp())
    # util.save_state(STATE)
    # TODO state based pings
    humans = [m for m in config.GUILD_ID.members if (not m.bot and (config.ADVERTISER_ROLE_ID in m.roles))]
    pinged = random.choice(humans)
    await pinged.send("Hello! You've been chosen to advertise for Legion this time! Please make sure to post something unique/fun in the Legion's Looking For Group post in the main bitcraft server!")
    print(f"Pinged {pinged.name} to advertise.")

@tasks.loop(minutes = 1)
async def ping_metronome():
    h = bot.get_user(201804073886941185)
    await h.send("HI METRONOME WE LOVE YOU")

@tasks.loop(time=config.ANNOY_TIME)
async def ticket_remind():
    humans = [m for m in config.GUILD_ID.members if (not m.bot and (TICKET_ROLE in m.roles))]
    for h in humans:
        date_check = datetime.now().replace(tzinfo=ZoneInfo("America/Chicago")) - h.joined_at.replace(tzinfo=ZoneInfo("America/Chicago"))
        if date_check.days > 7:
            await h.send(f"""
                It looks like you've been in the Legion discord for over a week without making a ticket.
                You have been automatically removed from the server to help maintain its cleanliness.
                If you believe this was in error, please rejoin the server and make a ticket.
            """)
            await h.kick()
            print(f"Kicked {h.name} for inactivity in ticket.")
        else:
            await h.send(f"""
                     Hi! You joined The Legion discord server for Bitcraft, but seem to have not made a ticket.
                     Please head to this channel: https://discord.com/channels/1267584422253694996/1317666800896577638
                     and click the ***Create ticket*** button at the top of the channel in order to finish the process of joining The Legion.
                     \n If you've already made a ticket, please make sure to read the questions in that channel and answer them in your created ticket.
                     \n Thank you for your cooperation :)
                     """)
        print(f"Pinged {h.name} to make a ticket.")

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("Sorry, you don't have the permissions to run that command.", ephemeral=True)
        return
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)
        return
    await interaction.followup.send(f"The bot has thrown the following error: {error}. Please contact Lanidae and send a screenshot of this message.", ephemeral=True)

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

bot.run(token)