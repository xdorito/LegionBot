import discord
import os
from datetime import time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# lets use dotenv to load environment variables
# and a role manager to return dev or prod roles
load_dotenv()
CURRENT_ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DISCORD_TOKEN = os.getenv('BOT_TOKEN')

DEVELOPEMENT = {
    "GUILD": {
        "id": 1267584422253694996,
        "object": discord.Object(id=1267584422253694996, type=discord.Guild),
    },
    "MEMBER": {
        "id": 1268739778119995505,
        "name": "Legionnaire"
    },
    "SENETOR": {
        "id": 1311824922301038632,
        "name": "Senator"
    },
    "ADMINISTRATOR": {
        "id": 1371792303206699040,
        "name": "Princeps"
    },
    "ADVERTISER": {
        "id": 1360478811661144114,
        "name": "Legion Advertiser"
    },
    "TICKET": {
        "id": 1324782094571798621,
        "name": "Ticket TIME"
    },
    "DISCIPLINARY": {
        "ids": [1367304039137542155, 1367304098659176641],
        "names": ["Bonked", "Pecunaria"]  # idk what these actually are
    },
    "PROFFESIONS": {
        "foraging": {
            "name": "Foraging",
            "id": 1267585190981796021
        },
        "hunting": {
            "name": "Hunting",
            "id": 1267585359986823168
        },
        "mining": {
            "name": "Mining",
            "id": 1267585386859728927
        },
        "forestry": {
            "name": "Forestry",
            "id": 1267585920773918752
        },
        "carpentry": {
            "name": "Carpentry",
            "id": 1267585436885323817
        },
        "leatherworking": {
            "name": "Leatherworking",
            "id": 1267585503385882665
        },
        "masonry": {
            "name": "Masonry",
            "id": 1267585535858315306
        },
        "smithing": {
            "name": "Smithing",
            "id": 1267585569442238556
        },
        "tailoring": {
            "name": "Tailoring",
            "id": 1267585594750402581
        },
        "scholar": {
            "name": "Scholar",
            "id": 1267585753496551627
        },
        "farming": {
            "name": "Farming",
            "id": 1267585784404377763
        },
        "fishing": {
            "name": "Fishing",
            "id": 1267585808186081311
        }
    }
}
PRODUCTION = {
    "GUILD": {
        "id": 1267584422253694996,
        "object": discord.Object(id=1267584422253694996, type=discord.Guild),
    },
    "MEMBER": {
        "id": 1268739778119995505,
        "name": "Legionnaire"
    },
    "SENETOR": {
        "id": 1311824922301038632,
        "name": "Senator"
    },
    "ADMINISTRATOR": {
        "id": 1371792303206699040,
        "name": "Princeps"
    },
    "ADVERTISER": {
        "id": 1360478811661144114,
        "name": "Legion Advertiser"
    },
    "TICKET": {
        "id": 1324782094571798621,
        "name": "Ticket TIME"
    },
    "DISCIPLINARY": {
        "ids": [1367304039137542155, 1367304098659176641],
        "names": ["Bonked", "Pecunaria"]  # idk what these actually are
    },
    "PROFFESIONS": {
        "foraging": {
            "name": "Foraging",
            "id": 1267585190981796021
        },
        "hunting": {
            "name": "Hunting",
            "id": 1267585359986823168
        },
        "mining": {
            "name": "Mining",
            "id": 1267585386859728927
        },
        "forestry": {
            "name": "Forestry",
            "id": 1267585920773918752
        },
        "carpentry": {
            "name": "Carpentry",
            "id": 1267585436885323817
        },
        "leatherworking": {
            "name": "Leatherworking",
            "id": 1267585503385882665
        },
        "masonry": {
            "name": "Masonry",
            "id": 1267585535858315306
        },
        "smithing": {
            "name": "Smithing",
            "id": 1267585569442238556
        },
        "tailoring": {
            "name": "Tailoring",
            "id": 1267585594750402581
        },
        "scholar": {
            "name": "Scholar",
            "id": 1267585753496551627
        },
        "farming": {
            "name": "Farming",
            "id": 1267585784404377763
        },
        "fishing": {
            "name": "Fishing",
            "id": 1267585808186081311
        }
    }
}

# Time settings
ANNOY_TIME = time(hour=0, minute=0, second=0, tzinfo=ZoneInfo("America/Chicago"))

# Bot settings
BOT_PREFIX = '$'
