import urllib
import asyncio
import aiohttp
import json
import re
import dotenv
import os
import sqlite3
from urllib.parse import quote_plus

from rich.traceback import install
from rich.console import Console
from rich.progress import track
from rich.theme import Theme
import asyncpraw
import topgg
import humor_langs
from discord.ext import commands
import discord

from utilities.helpers.help import Help_Embed
from utilities.helpers.utils import get_prefix
from discord.commands import Option
from cogs.utility import generate_meme  
from cogs.bot_commands import HelpOptions

license = """
MIT License

Copyright (c) 2021 Dhravya Shah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

# Standard libraries

# External libraries
# Rich Library for traceback, success and error messages, and progress bar


install()
dotenv.load_dotenv()

custom_theme = Theme({"success": "green", "error": "bold red"})

intents = discord.Intents.default()
intents.members = True  # Member intent for on_member join and leave
bot = commands.Bot(
    command_prefix=(get_prefix),
    description="""SpaceBot has many utility and fun commands that you can use! Also comes with music player!""",
    intents=intents,
    case_insensitive=True
)

# rich console object
bot.console = Console(theme=custom_theme)

# TOPGG client
bot.topggpy = topgg.DBLClient(
    bot,
    os.getenv("TOPGG_TOKEN"),
    autopost=True,
    post_shard_count=True,
)

# Asyncpraw reddit client
bot.reddit = asyncpraw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent="Spacebot",
)

# connecting to the database
bot.db = sqlite3.connect("database.db")

bot.dbcursor = bot.db.cursor()


async def session(bot):
    bot.httpsession = aiohttp.ClientSession()

asyncio.get_event_loop().run_until_complete(session(bot))


@bot.event
async def on_ready():
    print("Logged in as")
    bot.console.print(bot.user.name, style="success")
    bot.console.print(bot.user.id, style="success")
    print("------")
    await bot.change_presence(status=discord.Status.idle ,activity=discord.Game(name=f"on {len(bot.guilds)} servers, {len(list(bot.get_all_members()))} members. | .help"))


# loading cogs
files = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        files.append(f"cogs.{filename[:-3]}")
        pass
bot.load_extension('jishaku')
for file in track(files, description="Loading all cogs...."):
    bot.load_extension(file)

# *_____________________________________________________________________________

# TODO: SLASH COGS ARE HERE. MOVE THESE COMMANDS TO SLASH COGS


@bot.slash_command()
async def help(
        ctx):  # Passing a default value makes the argument optional
    """Get help about the most feature packed bot!!"""

    m = await ctx.respond(embed=Help_Embed(), view=HelpOptions())
    await asyncio.sleep(120)
    try:
        await m.edit("This help session expired", embed=None, view=None)
    except:
        pass


@bot.slash_command()
async def dev(ctx):
    """Get info about the developer of spacebot!"""
    em = discord.Embed(title="Contact the dev!!",
                       description="Do you want a personalised bot for your server?\n Or make a website? Or do cool Machine learning stuff? \nWell, then [contact me!!](https://discord.com/channels/@me/512885190251642891)")
    em.add_field(
        name="Website", value="[dhravya.github.io/portfolio-website](https://dhravya.github.io/portfolio-website)")
    em.add_field(
        name="Twitter", value="[@dhravyashah](https://twitter.com/dhravyashah)", inline=False)
    em.add_field(
        name="Github", value="[github/dhravya](https://github.com/dhravya)", inline=False)
    em.add_field(name="Check out spacebot!",
                 value="[Link to topgg page!](https://top.gg/bot/881862674051391499)\n[Link to website!](https://spacebot.ga)", inline=False)
    em.colour = discord.Colour.blue()
    em.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/Ll2Us9DHwiMJ_et5L5J2_4QkfXMjQ0WB1w6EYb3G4wI/%3Fv%3D1/https/cdn.discordapp.com/emojis/856078862852161567.png")
    await ctx.respond(embed=em)


@bot.slash_command()
async def whois(ctx, member: discord.Member = None):
    """gives info about member"""
    if not member:  # if member is no mentioned
        member = ctx.author  # set member as the author
    roles = [role for role in member.roles]
    embed = discord.Embed(
        colour=discord.Colour.orange(),
        title=str(member),
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="Display Name:", value=member.display_name)
    embed.add_field(name="ID:", value=member.id)

    embed.add_field(
        name="Created Account On:",
        value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
    )
    embed.add_field(
        name="Joined Server On:",
        value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
    )

    embed.add_field(
        name="Roles:", value="".join([role.mention for role in roles[1:]])
    )
    embed.add_field(name="Highest Role:", value=member.top_role.mention)
    await ctx.respond(embed=embed)


@bot.slash_command()
async def invite(ctx):
    """Invite spacebot to your server :)"""
    await ctx.resond("Invite spacebot now!! Use this link: https://dsc.gg/spacebt")


@bot.slash_command()
async def kick(ctx, user: discord.Member):
    """Kicks a user from the server."""
    if not ctx.author.guild_permissions.kick_members == True:
        return await ctx.respond("You dont have the permission to kick others -_-", ephemeral=True)
    if ctx.author == user:
        return await ctx.repond("You cannot kick yourself.", ephemeral=True)
    await user.kick()
    embed = discord.Embed(
        title=f"User {user.name} has been kicked.", color=0x00FF00
    )
    embed.add_field(name="Goodbye!", value=":boot:")
    try:
        embed.set_thumbnail(url=user.avatar.url)
    except:
        pass
    await ctx.respond(embed=embed)


@bot.slash_command()
async def ban(ctx, user: discord.Member):
    """Bans a user from the server."""
    if not ctx.author.guild_permissions.ban_members == True:
        return await ctx.respond("You dont have the permission to ban others -_-", ephemeral=True)
    if ctx.author == user:
        return await ctx.send("You cannot ban yourself.", ephemeral=True)
    await user.ban()
    embed = discord.Embed(
        title=f"User {user.name} has been banned.", color=0x00FF00
    )
    embed.add_field(name="Goodbye!", value=":hammer:")
    embed.set_thumbnail(url=user.avatar.url)
    await ctx.send(embed=embed)


@bot.slash_command()
async def mute(ctx, member: discord.Member, *, reason=None):
    """Mutes a user indefinitely"""
    if not ctx.author.guild_permissions.manage_messages == True:
        return await ctx.respond("You dont have the permission to mute others -_-", ephemeral=True)

    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(
                mutedRole,
                speak=False,
                send_messages=False,
                read_message_history=True,
                read_messages=False,
            )
    embed = discord.Embed(
        title="muted",
        description=f"{member.mention} was muted ",
        colour=discord.Colour.light_gray(),
    )
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" you have been muted from: {guild.name} reason: {reason}")


@bot.slash_command()
async def welcome_setup(ctx, channel: Option(discord.TextChannel, "Which channel to send a welcome message to?") = None,
                        should_dm: Option(str, "Should the welcome message be sent to the user?", choices=[
                                          "True", "False"]) = "False",
                        goodbye_message: Option(
                            str, "What message to send to the user and/or channel when they leave?") = None,
                        message: Option(str, "What message to send to the user and/or channel?") = None):
    """Sets up the welcome message for the server"""

    if not ctx.author.guild_permissions.manage_messages == True:
        return await ctx.respond("You dont have the permission to manage messages -_-", ephemeral=True)

    try:
        bot.dbcursor.execute(
            f"SELECT id FROM Servers WHERE id = {ctx.guild.id}")
    except KeyError:
        bot.dbcursor.execute(
            f"INSERT INTO Servers (id) VALUES ({ctx.guild.id})")

    if not channel:
        welcome_channel = None
    else:
        welcome_channel = channel.id

    if should_dm == "True":
        should_dm = 1
    else:
        should_dm = 0

    welcome_toggle = 1
    print("Its this one!")
    bot.dbcursor.execute(f"UPDATE Servers SET (welcome_toggle,welcome_channel,welcome_dm,goodbye_message,welcome_message) = (?,?,?,?,?) WHERE id = {ctx.guild.id}", (
        welcome_toggle, welcome_channel, should_dm, goodbye_message, message))
    await ctx.respond("Welcome message set up!", ephemeral=True)
    bot.db.commit()


@bot.slash_command()
async def unmute(ctx, user: discord.Member):
    """Unmutes a user."""

    if not ctx.author.guild_permissions.manage_messages == True:
        return await ctx.respond("You dont have the permission to unmute others -_-", ephemeral=True)

    rolem = discord.utils.get(ctx.guild.roles, name="Muted")
    if rolem not in user.roles:
        return await ctx.respond("User is not muted.", ephemeral=True)
    embed = discord.Embed(
        title=f"User {user.name} has been unmuted.", color=0x00FF00
    )
    embed.add_field(name="Welcome back!", value=":open_mouth:")
    # embed.set_thumbnail(url= user.avatar.url)
    await ctx.send(embed=embed)
    await user.remove_roles(rolem)


@bot.slash_command()
async def prune(ctx, count: int, member: discord.Member = None):
    """Deletes a specified amount of messages. (Max 100)"""
    if not ctx.author.guild_permissions.manage_messages == True:
        return await ctx.respond("You dont have the permission to delete messages -_-")

    if member:
        def check(m):
            return m.author == member
        await ctx.channel.purge(limit=100, check=check)
    else:
        count = max(1, min(count, 100))
        await ctx.channel.purge(limit=count, bulk=True)


@bot.slash_command()
async def clean(ctx):
    """Cleans the chat of the bot's messages."""
    if not ctx.author.guild_permissions.manage_messages == True:
        return await ctx.respond("You dont have the permission to delete messages -_-")

    def is_me(m):
        return m.author == bot.user
    await ctx.channel.purge(limit=100, check=is_me)


@bot.slash_command()
async def announce(ctx, *, text: str, description: str, channel: discord.TextChannel = None):
    """Sets an announcement to a particular channel. Please separate the title and description by a ,"""
    if not ctx.author.guild_permissions.manage_messages == True:
        return await ctx.respond("You dont have the permission to send messages -_-")
    if not channel:
        channel = ctx.channel
    # text = text.split(",")
    em = discord.Embed(title=text, description=description, colour=discord.Color.random(
    )).set_author(name=str(ctx.author.name), icon_url=str(ctx.author.avatar.url))
    await channel.send(embed=em)
    await ctx.respond("Announcement sent!!!")


@bot.slash_command()
async def suggestdev(ctx, *, suggestion: str):
    """Sends your message to the support server of the bot so that the community can discuss on your ideas!"""
    channel = bot.get_channel(896739923204374559)
    embed = discord.Embed(
        colour=discord.Color.blurple(),
        title=f"{ctx.author} Suggested:",
        description=suggestion,
    )
    await ctx.respond("Suggestion sent! Thank You!", embed=embed)
    suggested = await channel.send(embed=embed)
    await suggested.add_reaction("👍")
    await suggested.add_reaction("👎")


@bot.slash_command()
async def ascii(ctx, *, text: str):
    """Makes a fancy ascii art!"""
    async with bot.httpsession.get(
        f"http://artii.herokuapp.com/make?text={urllib.parse.quote_plus(text)}"
    ) as f:
        message = await f.text()
    if len("```" + message + "```") > 2000:
        await ctx.respond("Your ASCII is too long!")
        return
    await ctx.respond("```" + message + "```")


@bot.slash_command()
async def imagesearch(ctx, *, query):
    """Google image search. [p]i Lillie pokemon sun and moon"""
    if query[0].isdigit():
        item = int(query[0])
        query = query[1:]
    else:
        item = 0
    async with bot.httpsession.get("https://www.googleapis.com/customsearch/v1?q=" + urllib.parse.quote_plus(query) + "&start=" + '1' + "&key=" + os.getenv("GOOGLE_KEY") + "&cx=" + os.getenv("GOOGLE_CX") + "&searchType=image") as resp:
        if resp.status != 200:
            return await ctx.send('Google failed to respond.')
        else:
            result = json.loads(await resp.text())
            try:
                result['items']
            except:
                return await ctx.send('There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine.')
            if len(result['items']) < 1:
                return await ctx.send('There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine.')
            em = discord.Embed()
            try:
                em.set_image(url=result['items'][item]['link'])
                show_search = True
                if show_search:
                    em.set_footer(text="Search term: \"" + query + "\"")
                await ctx.respond(content=None, embed=em)
            except:
                await ctx.respond(result['items'][item]['link'])
                await ctx.respond("Search term: \"" + query + "\"")


@bot.slash_command()
async def tinyurl(ctx, link: str):
    """Compresses the size of url, powered by tinyurl"""
    url = "http://tinyurl.com/api-create.php?url=" + link

    async with bot.httpsession.get(url) as resp:
        new = await resp.text()
    emb = discord.Embed(color=discord.Colour.blurple())
    emb.add_field(name="Original Link", value=link, inline=False)
    emb.add_field(name="Shortened Link", value=new, inline=False)
    emb.set_footer(
        text="Powered by tinyurl.com",
        icon_url="http://cr-api.com/static/img/branding/cr-api-logo.png",
    )
    await ctx.respond(embed=emb)


@bot.slash_command()
async def covidinfo(ctx, country: str):
    """Get stats about coronavirus in various countries!"""

    ref = await bot.httpsession.get(
        f"https://disease.sh/v3/covid-19/countries/{country.lower()}"
    )
    r = await ref.json()

    json_data = [
        ("Total Cases", r["cases"]),
        ("Total Deaths", r["deaths"]),
        ("Total Recover", r["recovered"]),
        ("Total Active Cases", r["active"]),
        ("Total Critical Condition", r["critical"]),
        ("New Cases Today", r["todayCases"]),
        ("New Deaths Today", r["todayDeaths"]),
        ("New Recovery Today", r["todayRecovered"]),
    ]

    embed = discord.Embed(
        description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R>"
    )

    for name, value in json_data:
        embed.add_field(
            name=name, value=f"{value:,}" if isinstance(value, int) else value
        )

    await ctx.respond(
        f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
        f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
        embed=embed,
    )


@bot.slash_command()
async def meme(ctx):
    """Gets a random meme from various subreddits"""
    class MemeView(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label="Next Meme", emoji="👏", style=discord.ButtonStyle.green)
        async def next_meme(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.message.edit(embed=await generate_meme())
    await ctx.send(embed=await generate_meme(), view=MemeView())

# command to automaticallly generate cat pictures


@bot.slash_command()
async def cat(ctx):
    """Gets a random cute cat picture!"""
    async with bot.httpsession.get("https://api.thecatapi.com/v1/images/search") as resp:
        if resp.status != 200:
            return await ctx.send("Cat API failed to respond.")
        else:
            result = json.loads(await resp.text())
            try:
                result[0]['url']
            except:
                return await ctx.send("There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine.")
            emb = discord.Embed(color=discord.Colour.blurple())
            emb.set_image(url=result[0]['url'])
            await ctx.respond(embed=emb)

# command to automatically generate dog pictures


@bot.slash_command()
async def dog(ctx):
    """Who doesnt like dogs?!"""
    async with bot.httpsession.get("https://dog.ceo/api/breeds/image/random") as resp:
        if resp.status != 200:
            return await ctx.send("Dog API failed to respond.")
        else:
            result = json.loads(await resp.text())
            try:
                result['message']
            except:
                return await ctx.send("There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine.")
            emb = discord.Embed(color=discord.Colour.blurple())
            await ctx.respond(embed=emb.set_image(url=result['message']))


@bot.slash_command()
async def owofy(ctx, *, text: str):
    """Converts your message in UwUs. its not worth trying, trust me."""
    await ctx.respond(
        f"<:uwupwease:896107914849296414> {humor_langs.owofy(text)} <:uwupwease:896107914849296414>"
    )


@bot.slash_command()
async def ping(ctx):
    """Pong!"""
    await ctx.respond(f"Pong! {round(bot.latency * 1000)}ms")


@bot.slash_command()
async def thank(
    ctx: commands.Context,
    whom: discord.Member = None,
    *,
    reason=None,
):
    """Thank someone for their good deeds!"""
    if whom is None:
        await ctx.respond("Thank who? your mom?")
    if whom == ctx.author:
        return await ctx.respond("You cannot thank yourself! Idiot!")
    if whom.bot:
        return await ctx.respond("You can't thank bots!\nThank real people!")

    if reason is None:
        reason = "being an amazing person!"
    if reason.lower().startswith("for "):
        reason = reason[4:]

    return await ctx.respond(
        embed=discord.Embed(
            title=f":heart: Thank you!",
            description=f"Thank you {whom.mention} for {reason}",
        ).set_thumbnail(
            url="https://cdn.discordapp.com/emojis/856078862852161567.png?v=1"
        )
    )


@bot.slash_command()
async def youtube(ctx, *, query):

    html = urllib.request.urlopen(
        f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    await ctx.respond(f"https://www.youtube.com/watch?v={video_ids[0]}")


#!___________________________________________________________________________

# Running the bot
# bot.run(os.getenv("BOT_TOKEN"))

# for testing
bot.run(os.getenv("TEST_BOT_TOKEN"))