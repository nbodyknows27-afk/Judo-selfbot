import discord
from discord.ext import commands
import asyncio
import random
import os
import aiohttp

# ================= TOKEN =================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No token found in environment variables!")

# ================= GLOBALS =================
repeating = {}
thanked_users = set()

# ================= BOT SETUP =================
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=',',
    self_bot=True,
    intents=intents,
    help_command=None
)

async def delete_cmd(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f'{bot.user} loaded Nighty-style system')

@bot.after_invoke
async def thank_user(ctx):
    if ctx.author.id not in thanked_users:
        thanked_users.add(ctx.author.id)
        try:
            await ctx.send("***THANK YOU!!!*** thank you for using judo selfbot made by Th3scr1pt3r")
        except Exception as e:
            print(f"Thank you message failed: {e}")

# ================= HELP =================
@bot.command(aliases=["cmds", "commands"])
async def help(ctx):
    await delete_cmd(ctx)
    await ctx.send("""
🔥 Available Commands

,avatar [@user] - Shows a user's avatar
,ban @user [reason] - Bans a user
,banner [@user] - Shows a user's banner
,clear [amount] - Deletes messages
,gayrate [@user] - Rates how gay a user is
,gitsearch <query> - Search GitHub repos
,gituser <username> - GitHub user info
,guildicon - Shows server icon
,hack [@user] - Prank hack simulation
,iplookup <ip> - Lookup an IP address
,kick @user [reason] - Kicks a user
,loverate @user1 [@user2] - Love compatibility
,math <expression> - Evaluate math
,setnickname <name> - Change your nickname
,ping - Bot latency
,randomavatar - Random profile picture
,rep <message> - Repeat a message every 30s
,serverinfo - Server information
,spam <amount> <message> - Spam a message
,status <online/idle/dnd/invisible> <text> - Set status
,stop - Stop repeating
""")

# ================= AVATAR =================
@bot.command()
async def avatar(ctx, user: discord.Member = None):
    await delete_cmd(ctx)
    user = user or ctx.author
    await ctx.send(str(user.avatar_url))

# ================= BANNER =================
@bot.command()
async def banner(ctx, user: discord.Member = None):
    await delete_cmd(ctx)
    user = user or ctx.author
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://discord.com/api/v9/users/{user.id}",
            headers={"Authorization": TOKEN}
        ) as resp:
            data = await resp.json()
            banner_hash = data.get("banner")
            if banner_hash:
                ext = "gif" if banner_hash.startswith("a_") else "png"
                url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_hash}.{ext}?size=1024"
                await ctx.send(url)
            else:
                await ctx.send(f"{user} has no banner.")

# ================= GUILD ICON =================
@bot.command()
async def guildicon(ctx):
    await delete_cmd(ctx)
    if ctx.guild.icon:
        await ctx.send(str(ctx.guild.icon_url))
    else:
        await ctx.send("This server has no icon.")

# ================= SERVER INFO =================
@bot.command()
async def serverinfo(ctx):
    await delete_cmd(ctx)
    g = ctx.guild
    await ctx.send(f"**{g.name}**\nMembers: {g.member_count}\nOwner: {g.owner}\nRegion: {g.region}\nCreated: {g.created_at.strftime('%Y-%m-%d')}")

# ================= GIT SEARCH =================
@bot.command()
async def gitsearch(ctx, *, query):
    await delete_cmd(ctx)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.github.com/search/repositories?q={query}&per_page=3",
            headers={"Accept": "application/vnd.github.v3+json"}
        ) as resp:
            data = await resp.json()
            if not data.get("items"):
                return await ctx.send("No results found.")
            result = ""
            for repo in data["items"]:
                result += f"**{repo['full_name']}** ⭐{repo['stargazers_count']}\n{repo['html_url']}\n"
            await ctx.send(result)

# ================= GIT USER =================
@bot.command()
async def gituser(ctx, username):
    await delete_cmd(ctx)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.github.com/users/{username}",
            headers={"Accept": "application/vnd.github.v3+json"}
        ) as resp:
            if resp.status == 404:
                return await ctx.send("User not found.")
            data = await resp.json()
            await ctx.send(f"**{data['login']}** ({data.get('name', 'N/A')})\nRepos: {data['public_repos']} | Followers: {data['followers']} | Following: {data['following']}\nBio: {data.get('bio', 'N/A')}\nURL: {data['html_url']}")

# ================= IP LOOKUP =================
@bot.command()
async def iplookup(ctx, ip):
    await delete_cmd(ctx)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://ip-api.com/json/{ip}") as resp:
            data = await resp.json()
            if data.get("status") == "fail":
                return await ctx.send("Invalid IP or lookup failed.")
            await ctx.send(f"**IP:** {data['query']}\n**Country:** {data.get('country', 'N/A')}\n**Region:** {data.get('regionName', 'N/A')}\n**City:** {data.get('city', 'N/A')}\n**ISP:** {data.get('isp', 'N/A')}")

# ================= RANDOM AVATAR =================
@bot.command()
async def randomavatar(ctx):
    await delete_cmd(ctx)
    seed = random.randint(1, 99999)
    await ctx.send(f"https://robohash.org/{seed}.png?size=256x256")

# ================= SET NICKNAME =================
@bot.command()
async def setnickname(ctx, *, name):
    await delete_cmd(ctx)
    try:
        await ctx.author.edit(nick=name)
        await ctx.send(f"Nickname set to **{name}**")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# ================= STATUS =================
@bot.command()
async def status(ctx, state, *, text=None):
    await delete_cmd(ctx)
    states = {
        "online": discord.Status.online,
        "idle": discord.Status.idle,
        "dnd": discord.Status.dnd,
        "invisible": discord.Status.invisible
    }
    if state not in states:
        return await ctx.send("Valid options: online, idle, dnd, invisible")
    activity = discord.Game(name=text) if text else None
    await bot.change_presence(status=states[state], activity=activity)
    await ctx.send(f"Status set to **{state}**" + (f" | {text}" if text else ""))

# ================= REP =================
@bot.command(aliases=["repeat", "loop"])
async def rep(ctx, *, msg):
    await delete_cmd(ctx)
    if ctx.channel.id in repeating:
        return await ctx.send("Already running")
    repeating[ctx.channel.id] = True
    while repeating.get(ctx.channel.id):
        await ctx.send(msg)
        await asyncio.sleep(30)

@bot.command(aliases=["end", "halt"])
async def stop(ctx):
    await delete_cmd(ctx)
    repeating.pop(ctx.channel.id, None)

# ================= SPAM =================
@bot.command(aliases=["flood", "blast"])
async def spam(ctx, amount: int, *, msg):
    await delete_cmd(ctx)
    for _ in range(amount):
        await ctx.send(msg)
        await asyncio.sleep(1)

# ================= FUN =================
@bot.command(aliases=["gay", "rate"])
async def gayrate(ctx, user: discord.Member = None):
    await delete_cmd(ctx)
    user = user or ctx.author
    await ctx.send(f"{user} is {random.randint(0,100)}% gay 🌈")

@bot.command(aliases=["love", "ship"])
async def loverate(ctx, u1: discord.Member, u2: discord.Member = None):
    await delete_cmd(ctx)
    u2 = u2 or ctx.author
    await ctx.send(f"❤️ {u1} + {u2} = {random.randint(0,100)}%")

@bot.command(aliases=["hackuser", "ipgrab"])
async def hack(ctx, user: discord.Member = None):
    await delete_cmd(ctx)
    user = user or ctx.author
    steps = ["Finding IP...", "Cracking password...", "Injecting malware...", "Done."]
    for s in steps:
        await ctx.send(s)
        await asyncio.sleep(1)

# ================= UTIL =================
@bot.command(aliases=["p"])
async def ping(ctx):
    await delete_cmd(ctx)
    await ctx.send(f"{round(bot.latency*1000)}ms")

@bot.command(aliases=["calc"])
async def math(ctx, *, expr):
    await delete_cmd(ctx)
    try:
        await ctx.send(eval(expr))
    except:
        await ctx.send("Error")

# ================= MOD =================
@bot.command(aliases=["purge", "wipe"])
async def clear(ctx, amount: int = 5):
    await delete_cmd(ctx)
    deleted = 0
    async for message in ctx.channel.history(limit=100):
        if deleted >= amount:
            break
        if message.author == ctx.author:
            await message.delete()
            deleted += 1
            await asyncio.sleep(0.5)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await delete_cmd(ctx)
    try:
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await delete_cmd(ctx)
    try:
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# ================= RUN =================
bot.run(TOKEN, bot=False)
