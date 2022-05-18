import time
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

class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        

    async def setup_hook(self):
        self.loop.create_task(app.run_task(port= 7070,debug=True)) 
async def get_prefix(client, message):
    try:
      defualt_prefix = "skye "
      if not message.guild:
        return commands.when_mentioned_or(defualt_prefix)(client, message)

      prefix = await bot.db.fetch('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)
      if len(prefix) == 0:
        await bot.db.execute('INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2)', message.guild.id, defualt_prefix)
      else: 
          prefix = prefix[0].get("prefix")

    
      return commands.when_mentioned_or(prefix, defualt_prefix)(client,message)
    except TypeError:
      pass

async def create_db_pool():
        bot.db = await asyncpg.create_pool(dsn="postgres://skye:GRwe2h2ATA5qrmpa@localhost:5432/skye", ssl=ssl_object)
        print('Connection to POSTGRESQL')

app = Quart(__name__)
bot = MyBot(command_prefix="12",intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("hi")

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
            "rest":int(ping)
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
    
async def main():
    async with bot:
        bot.wait_until_ready
    
        await create_db_pool()
        await bot.start(token)

asyncio.run(main())