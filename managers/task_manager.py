from datetime import datetime, timedelta
import random
import config
from discord.ext import tasks
from managers.state_manager import BotStateManager
from managers.roles_manager import BotRolesManager


class BotTasksManager:
    def __init__(self, bot):
        self.bot = bot
        self.state_manager: BotStateManager = self.bot.state_manager
        self.roles_manager: BotRolesManager = self.bot.roles_manager

    @tasks.loop(minutes=67)
    async def legion_advert(self):
        if int(datetime.now().timestamp()) - self.state_manager.state.get('LAST_ANNOUNCE') < 57600:
            return
        self.state_manager.update_state({'LAST_ANNOUNCE': int(datetime.now().timestamp())})
        advertiser = self.roles_manager.get_members_by_role("Legion Advertiser")
        pinged = random.choice(advertiser)
        await pinged.send(
            "Hello! You've been chosen to advertise for Legion this time! Please make sure to post something unique/fun in the Legion's Looking For Group post in the main bitcraft server!")
        print(f"Pinged {pinged.name} to advertise.")

    @tasks.loop(minutes=1)
    async def ping_metronome(self):
        h = self.bot.get_user(201804073886941185)
        await h.send("HI METRONOME WE LOVE YOU")

    @tasks.loop(time=config.ANNOY_TIME)
    async def ticket_remind(self):
        unverified_members = self.roles_manager.get_members_by_role("Ticket Time")
        for m in unverified_members:
            date_check = datetime.now() - m.joined_at
            if date_check > timedelta(days=7):
                await m.send(f"""
                    It looks like you've been in the Legion discord for over a week without making a ticket.
                    You have been automatically removed from the server to help maintain its cleanliness.
                    If you believe this was in error, please rejoin the server and make a ticket.
                """)
                # TODO verify default intents allow kicking
                await m.kick()
                print(f"Kicked {m.name} for inactivity in ticket.")
            else:
                await m.send(f"""
                         Hi! You joined The Legion discord server for Bitcraft, but seem to have not made a ticket.
                         Please head to this channel: https://discord.com/channels/1267584422253694996/1317666800896577638
                         and click the ***Create ticket*** button at the top of the channel in order to finish the process of joining The Legion.
                         \n If you've already made a ticket, please make sure to read the questions in that channel and answer them in your created ticket.
                         \n Thank you for your cooperation :)
                         """)
            print(f"Pinged {m.name} to make a ticket.")

