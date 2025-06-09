import os
import database_sqlite
from tasks import BotTasks
from state_manager import BotStateManager
import config
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(config.BOT_PREFIX, intents=intents)
bot.config = config
bot.state_manager = BotStateManager()

db = database_sqlite.DatabaseSqlite()
db.setup_db()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    #  load cogs
    for file in os.listdir('./cogs'):
        if file.endswith('.py') and not file.startswith('__'):
            filename = f'cogs.{file[:-3]}'
            try:
                await bot.load_extension(f'cogs.{filename}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

    # Initialize bot tasks
    bot_tasks = BotTasks(bot)
    bot_tasks.ticket_remind.start()
    bot_tasks.legion_advert.start()


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
