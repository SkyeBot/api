import datetime
import time
from typing import Optional
from quart import Quart, render_template, request, jsonify
import discord
from discord.ext import commands
import asyncio
import asyncpg
from config import token

import ssl
ssl_object = ssl.create_default_context()
ssl_object.check_hostname = False
ssl_object.verify_mode = ssl.CERT_NONE

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        self._connected = False
        self.startup_time: Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        super().__init__(*args, **kwargs)
    
    async def on_ready(self):
        if self._connected:
            msg = f"Bot reconnected at {datetime.now().strftime('%b %d %Y %H:%M:%S')}"
            print(msg)        
        else:
            self._connected = True
            self.startup_time = discord.utils.utcnow() - self.start_time
            msg = (
                f"Successfully logged into {self.user}. ({round(self.latency * 1000)}ms)\n"
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
            )
            print(msg)

    async def setup_hook(self):
        self.loop.create_task(app.run_task(port= 6060,debug=True)) 


async def get_prefix(client, message):
    try:
        defualt_prefix = "skye "
        if not message.guild:
            return commands.when_mentioned_or(defualt_prefix)(client, message)

        prefix = await bot.db.fetchrow('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)


        a = prefix.get("prefix")
        print(a)
    
        return commands.when_mentioned_or(a, defualt_prefix)(client,message)
    except TypeError:
      pass

async def create_db_pool():
        bot.db = await asyncpg.create_pool(dsn="postgres://skye:GRwe2h2ATA5qrmpa@localhost:5432/skye", ssl=ssl_object)
        print('Connection to POSTGRESQL')

app = Quart(__name__)
bot = MyBot(intents=discord.Intents.all())


@app.route("/bot/stats")
async def api():
    avgmembers = sum(g.member_count for g in bot.guilds) / len(bot.guilds)
    before = time.monotonic()
    before_ws = int(round(bot.latency * 1000, 1))
    ping = (time.monotonic() - before) * 1000
    data = {
        "@me":{
                "status":f"{bot.status}",
                "username":f"{bot.user.name}",
                "id":f"{bot.user.id}",
                "discriminator":f"{bot.user.discriminator}",
                "avatar":f"{bot.user.avatar}",

        },
        "servers": len(bot.guilds),
        "users": len(bot.users),
        "avg_users_server":f"{avgmembers:.2f}",
        "ping": {
            "type":"ws",
            "ws":before_ws,
            "rest":f"{int(round(bot.latency * 1000))}"
        },
    }

    return jsonify(data)
        

@app.route("/bot/servers", methods=['GET'])
async def servers():
    id = request.args.get('id', default = None, type = int)
    
    if id is None:
        return 'No id!'

    server = bot.get_guild(id)
    starboard = await bot.db.fetchrow("SELECT channel_id FROM starboard WHERE guild = $1", server.id)
    if starboard is None:
        star = False
    else:
        star = True
    boosters = server.premium_subscription_count
    prefix_fetch = await bot.db.fetchrow("SELECT prefix FROM GUILDS WHERE guild_id = $1", server.id)

    prefix = prefix_fetch.get("prefix")
    print(prefix)
    if boosters == None:
        return "None"
    

    data  = {
        f"{server.name}":{
                "server_id":f"{server.id}",
                "owner_id":f"{server.owner_id}",
                "server_avatar":f"{server.icon.url}",
                "member_count":f"{server.member_count}",
                "premium_users":f"{boosters}",
                "premium_level":f"{server.premium_tier}"
        },
        "database":{
            "prefix": prefix,
            "active_starboard": star
        }
    }

    return jsonify(data)

@app.route('/bot/users')
async def users():
    id = request.args.get('id', default = None, type = int)
    user = await bot.fetch_user(id)
    guild_ids = []
    for guild in user.mutual_guilds:
        guild_ids.append(guild.id)
    data = {
        f"{user.name}#{user.discriminator}":{
            "id":f"{user.id}",
            "discriminator":user.discriminator,
            "avatar":user.avatar.url,
            "banner":user.banner.url 
        },
        "mutual_guilds":guild_ids
    }

    return jsonify(data)
        
async def main():
    async with bot:
        bot.wait_until_ready
    
        await create_db_pool()
        await bot.start(token)

asyncio.run(main())