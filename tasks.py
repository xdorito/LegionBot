from datetime import datetime
import random
from zoneinfo import ZoneInfo
import config
from discord.ext import tasks


class BotTasks:
    def __init__(self, bot):
        self.bot = bot
        self.state_manager = bot.state_manager

    @tasks.loop(minutes=67)
    async def legion_advert(self):
        if int(datetime.now().timestamp()) - self.state_manager.get('LAST_ANNOUNCE') < 57600:
            return
        self.state_manager.update_state({'LAST_ANNOUNCE': int(datetime.now().timestamp())})
        humans = [m for m in config.GUILD_ID.members if (not m.bot and (config.ADVERTISER_ROLE_ID in m.roles))]
        pinged = random.choice(humans)
        await pinged.send(
            "Hello! You've been chosen to advertise for Legion this time! Please make sure to post something unique/fun in the Legion's Looking For Group post in the main bitcraft server!")
        print(f"Pinged {pinged.name} to advertise.")

    @tasks.loop(minutes=1)
    async def ping_metronome(self):
        h = self.bot.get_user(201804073886941185)
        await h.send("HI METRONOME WE LOVE YOU")

    @tasks.loop(time=config.ANNOY_TIME)
    async def ticket_remind(self):
        humans = [m for m in config.GUILD_ID.members if (not m.bot and (config.TICKET_ROLE_ID in m.roles))]
        for h in humans:
            date_check = datetime.now().replace(tzinfo=ZoneInfo("America/Chicago")) - h.joined_at.replace(
                tzinfo=ZoneInfo("America/Chicago"))
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

