import asyncio
import os
import random
import aiohttp
import json
import re
import io

import discord
from discord.ext import commands
from discord.ext.commands import BucketType
from datetime import datetime
import humor_langs
import wikipedia
import asyncpraw
import urllib.parse
import ffmpy
import textwrap
from translate import Translator
from PyDictionary import PyDictionary
from udpy import UrbanClient
import xml.etree.ElementTree as ET
from googlesearch import search
import names

from urllib.parse import quote_plus
import qrcode
from qrcode.exceptions import DataOverflowError
from qrcode.image import styledpil, styles
import inspect, operator
from typing import Literal

from utilities.helpers import checks
from utilities.helpers.qrgenerator import MessagePredicate
from utilities.helpers.utils import *

full = names.get_full_name
first = names.get_first_name
last = names.get_last_name

translatorf = Translator(from_lang="fr", to_lang="en")
translatorg = Translator(from_lang="de", to_lang="en")
dictionary = PyDictionary()
ud = UrbanClient()


async def generate_meme():
    subreddits = [
        "dankmemes",
        "memes"
    ]
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT"),
        client_secret=os.getenv("REDDIT_SECRET"),
        user_agent="Spacebot",
    )

    subreddit = await reddit.subreddit(random.choice(subreddits))

    all_subs = []
    async for submission in subreddit.hot(limit=20):
        if not submission.over_18:
            all_subs.append(submission)

    random_sub = random.choice(all_subs)
    name = random_sub.title
    url = random_sub.url
    em = discord.Embed(
        colour=discord.Colour.blurple(),
        title=name,
        url=f"https://reddit.com/{random_sub.id}",
    )
    em.set_image(url=url)
    em.set_footer(text=f"Taken from r/{subreddit}, Score = {random_sub.score}")
    await reddit.close()
    return em


_EXCLUDED_COLOURS = (
    # These colors are excluded from showing as examples,
    # but they may still be used in the generation of
    # QR codes.
    "dark_theme" "darker_grey",
    "darker_gray",
    "lighter_grey",
    "lighter_gray",
    "greyple",
    "random",  # already included
    "default",
    "from_hsv",
    "from_rgb",
)
RANDOM_COLOURS = list(
    filter(
        lambda x: (obj := getattr(discord.Colour, x, None))
        and inspect.ismethod(obj)
        and x not in _EXCLUDED_COLOURS,
        dir(discord.Colour),
    )
)

DEFAULT_OPENING_MESSAGE = """
Your message "{0}" will be converted into a QR code, but first you can customize how your QR code looks.
Customization does **not** prevent QR codes from working as intended.

Would you rather be able to change the colours, or the pattern of your QR code?
You can also go with option 3 if you want the default QR code style.

`1:` Colour Focused
`2:` Pattern Focused
`3:` Skip to default

**Send your message as the corresponding number**
""".strip()

DEFAULT_DRAWER_MESSAGE = """
Please provide a number from 1 to 6 based on the style you'd like.
If you want the 'classic' QR code style, `1` is the option you'd want to go for.

Fear not, none of these styles will prevent the QR code from working.

`1:` Squares (most common)
`2:` Gapped Squares
`3:` Circled
`4:` Rounded
`5:` Vertical bars
`6:` Horizontal bars

**Send your message as the corresponding number**
""".strip()

DEFAULT_MASK_MESSAGE = """
Please also provide a number from 1 to 5 based on the color mask you'd like.
If you want the 'classic' QR code style, `1` is the option you'd want to go for.

`1:` Solid black fill (most common, recommended)
`2:` Radial Gradient
`3:` Square Gradient
`4:` Horizontal Gradient
`5:` Vertical Gradient

**Send your message as the corresponding number**
""".strip()

DEFAULT_COLOR_MESSAGE_HEADER = "Please provide a **{0}** colour.\n"
DEFAULT_COLOR_MESSAGE = (
    lambda: f"""
This should be provided as a hex code.

Make sure this colour is differentiable.
Refrain from using colours that would prevent the QR code from working reliably.

**Examples**

- `{discord.Colour(random.randint(0x000000, 0xFFFFFF))}`
- `{discord.Colour(random.randint(0x000000, 0xFFFFFF))}`
- `{random.choice(RANDOM_COLOURS).replace("_", " ")}`
- `random`

**Your next message should be a colour of your choice**
""".strip()
)


class ColourConverter(commands.ColourConverter):
    async def convert(self, ctx, argument: str):
        extra_map = {"black": 0, "white": 16777215}
        try:
            original_arg = await super().convert(ctx, argument)
        except commands.BadColourArgument:
            for key, value in extra_map.items():
                if argument.lower() == key:
                    return discord.Colour(value)

            raise

        else:
            return original_arg


class Utility(commands.Cog, name="utilities", description="Useful stuff"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.topggpy = bot.topggpy
        self.session = bot.httpsession
        self.reddit = bot.reddit
        self.styles = {
            "drawers": {
                1: styles.moduledrawers.SquareModuleDrawer(),
                2: styles.moduledrawers.GappedSquareModuleDrawer(),
                3: styles.moduledrawers.CircleModuleDrawer(),
                4: styles.moduledrawers.RoundedModuleDrawer(),
                5: styles.moduledrawers.VerticalBarsDrawer(),
                6: styles.moduledrawers.HorizontalBarsDrawer(),
            },
            "masks": {
                1: styles.colormasks.SolidFillColorMask(),
                2: styles.colormasks.RadialGradiantColorMask(),
                3: styles.colormasks.SquareGradiantColorMask(),
                4: styles.colormasks.HorizontalGradiantColorMask(),
                5: styles.colormasks.VerticalGradiantColorMask(),
            },
        }

    async def convert_colour(self, ctx: commands.Context, content: str):
        colour_converter = ColourConverter()
        try:
            ret = await colour_converter.convert(ctx, content)
        except commands.BadArgument:
            ret = f'Failed to identify a colour from "{content}" - please start over.'
        finally:
            return ret

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        em = discord.Embed()
        em.title = f"Error: {__name__}"
        em.description = f"{error}"
        em.color = 0xEE0000
        await ctx.send(embed=em)
        me = self.bot.get_user(881861601756577832)
        await me.send(str(ctx.channel.id), embed=em)

    async def get_colour_data(self, ctx, shade: Literal["background", "fill"]):
        check = lambda x: all(
            operator.eq(getattr(ctx, y), getattr(x, y)) for y in ("author", "channel")
        )
        message = DEFAULT_COLOR_MESSAGE_HEADER.format(shade) + DEFAULT_COLOR_MESSAGE()
        await ctx.send(message)

        try:
            message = await self.bot.wait_for("message", check=check, timeout=100)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond, please start over.")
            return False
        else:
            color = await self.convert_colour(ctx, message.content)
            if not isinstance(color, discord.Colour):
                await ctx.send(color)
                return False

            return {f"{shade[:4]}_color": color.to_rgb()}

    async def get_style_data(self, ctx, style_type: Literal["drawers", "masks"]):
        mapper = {
            "drawers": {
                "message": DEFAULT_DRAWER_MESSAGE,
                "kwarg_key": "module_drawer",
            },
            "masks": {"message": DEFAULT_MASK_MESSAGE, "kwarg_key": "color_mask"},
        }
        pred = lambda x: MessagePredicate.contained_in(list(map(str, range(1, x + 1))))
        await ctx.send(mapper[style_type]["message"])
        try:
            check = pred(len(self.styles[style_type]))
            message = await self.bot.wait_for("message", check=check, timeout=100)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond, please start over.")
            return False
        else:
            return {
                mapper[style_type]["kwarg_key"]: self.styles[style_type][
                    int(message.content)
                ]
            }

    async def check_voted(self, userid):
        return await self.bot.topggpy.get_user_vote(userid)

    @commands.group(
        aliases=["server", "sinfo", "si"],
        pass_context=True,
        invoke_without_command=True,
    )
    async def serverinfo(self, ctx, *, msg=""):
        """Various info about the server. [p]help server for more info."""
        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())
        if ctx.invoked_subcommand is None:
            if msg:
                server = None
                try:
                    float(msg)
                    server = self.bot.get_guild(int(msg))
                    if not server:
                        return await ctx.send("Server not found.")
                except:
                    for i in self.bot.guilds:
                        if i.name.lower() == msg.lower():
                            server = i
                            break
                    if not server:
                        return await ctx.send(
                            "Could not find server. Note: You must be a member of the server you are trying to search."
                        )
            else:
                server = ctx.message.guild

            online = 0
            for i in server.members:
                if (
                    str(i.status) == "online"
                    or str(i.status) == "idle"
                    or str(i.status) == "dnd"
                ):
                    online += 1
            all_users = []
            for user in server.members:
                all_users.append("{}#{}".format(user.name, user.discriminator))
            all_users.sort()
            all = "\n".join(all_users)

            channel_count = len(
                [x for x in server.channels if type(x) == discord.channel.TextChannel]
            )

            role_count = len(server.roles)
            emoji_count = len(server.emojis)
            members = server.members
            bots = filter(lambda m: m.bot, members)
            bots = set(bots)

            em = discord.Embed(color=0xEA7938)
            em.add_field(name="Name", value=server.name)
            em.add_field(name="Owner", value=server.owner, inline=False)
            em.add_field(name="Members", value=server.member_count)
            em.add_field(name="Currently Online", value=online)
            em.add_field(name="Text Channels", value=str(channel_count))
            em.add_field(name="Region", value=server.region)
            em.add_field(
                name="Verification Level", value=str(server.verification_level)
            )
            # em.add_field(name='Highest role', value=server.rol)
            em.add_field(name="Number of roles", value=str(role_count))
            em.add_field(name="Number of emotes", value=str(emoji_count))
            # hastebin_of_users = '[List of all {} users in this server]({})'.format(server.member_count)
            em.add_field(name="Users", value=server.member_count)
            em.add_field(
                name="Created At",
                value=server.created_at.__format__("%A, %d. %B %Y @ %H:%M:%S"),
            )
            em.add_field(name="Bots Online", value=str(len(bots)))
            em.set_thumbnail(url=server.icon.url)
            em.set_author(name="Server Info", icon_url=ctx.author.avatar.url)
            em.set_footer(text="Server ID: %s" % server.id)
            await ctx.send(embed=em)

    @commands.command(aliases=["channel", "cinfo", "ci"], pass_context=True, no_pm=True)
    async def channelinfo(self, ctx, *, channel: int = None):
        """Shows channel information"""
        if not channel:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(channel)
        data = discord.Embed()
        if hasattr(channel, "mention"):
            data.description = "**Information about Channel:** " + channel.mention
        if hasattr(channel, "changed_roles"):
            if len(channel.changed_roles) > 0:
                data.color = (
                    discord.Colour.green()
                    if channel.changed_roles[0].permissions.read_messages
                    else discord.Colour.red()
                )
        if isinstance(channel, discord.TextChannel):
            _type = "Text"
        elif isinstance(channel, discord.VoiceChannel):
            _type = "Voice"
        else:
            _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id, inline=False)
        if hasattr(channel, "position"):
            data.add_field(name="Position", value=channel.position)
        if isinstance(channel, discord.VoiceChannel):
            if channel.user_limit != 0:
                data.add_field(
                    name="User Number",
                    value="{}/{}".format(
                        len(channel.voice_members), channel.user_limit
                    ),
                )
            else:
                data.add_field(
                    name="User Number", value="{}".format(len(channel.voice_members))
                )
            userlist = [r.display_name for r in channel.members]
            if not userlist:
                userlist = "None"
            else:
                userlist = "\n".join(userlist)
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif isinstance(channel, discord.TextChannel):
            try:
                pins = await channel.pins()
                data.add_field(name="Pins", value=len(pins), inline=True)
            except discord.Forbidden:
                pass
            data.add_field(name="Members", value="%s" % len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            hidden = []
            allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages is True:
                    if role.name != "@everyone":
                        allowed.append(role.mention)
                elif role.permissions.read_messages is False:
                    if role.name != "@everyone":
                        hidden.append(role.mention)
            if len(allowed) > 0:
                data.add_field(
                    name="Allowed Roles ({})".format(len(allowed)),
                    value=", ".join(allowed),
                    inline=False,
                )
            if len(hidden) > 0:
                data.add_field(
                    name="Restricted Roles ({})".format(len(hidden)),
                    value=", ".join(hidden),
                    inline=False,
                )
        if channel.created_at:
            data.set_footer(
                text=(
                    "Created on {} ({} days ago)".format(
                        channel.created_at.strftime("%d %b %Y %H:%M"),
                        (ctx.message.created_at - channel.created_at).days,
                    )
                )
            )
        await ctx.send(embed=data)

    @commands.command(aliases=["m"])
    async def math(self, ctx, operation, *nums):
        nums = list(map(int, nums))
        if operation == "add" or operation == "+":
            total = nums[0]
            for x in range(len(nums) - 1):
                total = total + nums[x + 1]
            await ctx.send(f"{total}")
        elif operation == "subtract" or operation == "-":
            total = nums[0]
            for x in range(len(nums) - 1):
                total = total - nums[x + 1]
            await ctx.send(f"{total}")
        elif operation == "multiply" or operation == "*" or operation == "x":
            total = nums[0]
            for x in range(len(nums) - 1):
                total = total * nums[x + 1]
            await ctx.send(f"{total}")
        elif operation == "divide" or operation == "/":
            total = nums[0]
            for x in range(len(nums) - 1):
                total = total / nums[x + 1]
            await ctx.send(f"{total}")

    @commands.command(name="joined")
    async def joined(self, ctx: commands.Context, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(
            "{0.name} joined in {0.joined_at} <:thinksmart:885480596510507008>".format(
                member
            )
        )

    @commands.command(name="morse")
    async def morse(self, ctx: commands.Context, *, query):
        await ctx.message.delete()
        await ctx.send(
            f"{ctx.message.author} said something in morse\n`"
            + encrypt(query.upper())
            + "`"
        )

    @commands.command()
    async def unmorse(self, ctx, *, query):
        await ctx.reply(f"{ctx.message.author},That means\n`" + decrypt(query) + "`")

    @commands.command(
        name="choose", description="For when you wanna settle the score some other way"
    )
    async def choose(self, ctx: commands.Context, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send("<:discordthink:885480932117737492> " + random.choice(choices))

    @commands.command(ame="translatef")
    async def translatef(self, ctx: commands.Context, *, message: str):
        """translates from french to english"""
        await ctx.send(
            f"{translatorf.translate(message).format(message)} :french_bread:"
        )

    @commands.command(name="translateg")
    async def translateg(self, ctx: commands.Context, *, message: str):
        """translates from german to english"""
        await ctx.send(
            f"{translatorg.translate(message).format(message)} :pinched_fingers:"
        )

    @commands.command(name="clap")
    async def clap(self, ctx: commands.Context, *, message: str):
        """converts the message into :clap: claps :clap:"""
        await ctx.send(humor_langs.clap_emojifier(message))

    @commands.command(name="text_to_emoji")
    async def text_to_emoji(self, ctx: commands.Context, *, message: str):
        """why do you need an explaination to this, dumbo"""
        await ctx.send(humor_langs.text_to_emoji(message))

    @commands.command(aliases=["member_count", "count"])
    async def members(self, ctx):
        embed = discord.Embed(colour=discord.Colour.orange())

        embed.set_author(name="Member Count", icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Current Member Count:", value=ctx.guild.member_count)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon.url)
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.command()
    async def whois(self, ctx, member: discord.Member = None):
        """gives info about member"""
        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())
        if not member:  # if member is no mentioned
            member = ctx.message.author  # set member as the author
        roles = [role for role in member.roles]
        embed = discord.Embed(
            colour=discord.Colour.orange(),
            timestamp=ctx.message.created_at,
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
        await ctx.send(embed=embed)

    @commands.command()
    async def google(self, ctx: commands.Context, *, query: str):
        """Returns a google link for a query"""
        answer = []
        for j in search(query, tld="co.in", num=10, stop=10, pause=2):
            answer.append(j)
        embed = discord.Embed(
            title="Google Result for: `" + query + "`:",
            description=str(answer).replace(",", "\n"),
        )
        await ctx.send(embed=embed, view=Google(query))
        answer.clear()

    @property
    def reactions(self):
        return {
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟",
        }

    @commands.command(aliases=["suggestion", "suggest"])
    async def poll(self, ctx, *, suggestion: str):
        """creates a poll with 2 choices"""
        embed = discord.Embed(description=suggestion)
        embed.set_author(
            name=f"Poll by {ctx.author.display_name}", icon_url=ctx.author.avatar.url
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = payload.member
        if user.bot:
            return
        msg = (
            await self.bot.get_guild(payload.guild_id)
            .get_channel(payload.channel_id)
            .fetch_message(payload.message_id)
        )
        emoji = payload.emoji
        users = []
        if msg.author.bot and ("👍" and "👎") in [str(i) for i in msg.reactions]:
            for react in msg.reactions:
                if str(react) == "👍":
                    async for reactor in react.users():
                        if reactor.bot:
                            continue
                        if reactor in users:
                            await msg.remove_reaction(emoji, user)
                            return
                        users.append(reactor)
                elif str(react) == "👎":
                    async for reactor in react.users():
                        if reactor.bot:
                            continue
                        if reactor in users:
                            await msg.remove_reaction(emoji, user)
                            return
                    return

    @commands.command()
    async def multi_choice(self, ctx, desc: str, *choices):
        """creates a poll with multiple choices"""

        if len(choices) < 2:
            ctx.command.reset_cooldown(ctx)
            if len(choices) == 1:
                return await ctx.send("Can't make a poll with only one choice")
            return await ctx.send(
                "You have to enter two or more choices to make a poll"
            )

        if len(choices) > 10:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You can't make a poll with more than 10 choices")

        embed = discord.Embed(
            description=f"**{desc}**\n\n"
            + "\n\n".join(
                f"{str(self.reactions[i])}  {choice}"
                for i, choice in enumerate(choices, 1)
            ),
            timestamp=datetime.datetime.utcnow(),
            color=discord.colour.Color.gold(),
        )
        embed.set_footer(text=f"Poll by {str(ctx.author)}")
        msg = await ctx.send(embed=embed)
        for i in range(1, len(choices) + 1):
            await msg.add_reaction(self.reactions[i])

    @commands.command(description="Define a word")
    async def define(self, ctx, *, word):
        await ctx.send(
            f"<:thinksmart:885480596510507008> meaning of {word} is {dictionary.meaning(word)}"
        )

    @commands.command(description="Get Synonym")
    async def synonym(self, ctx, *, word):
        await ctx.send(
            f"<:thinksmart:885480596510507008> {synonyms(word)}<:thinksmart:885480596510507008>"
        )

    @commands.command()
    async def tinyurl(self, ctx, *, link: str):
        """Makes a link shorter using the tinyurl api"""
        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())
        url = "http://tinyurl.com/api-create.php?url=" + link

        async with self.session.get(url) as resp:
            new = await resp.text()
        emb = discord.Embed(color=discord.Colour.blurple())
        emb.add_field(name="Original Link", value=link, inline=False)
        emb.add_field(name="Shortened Link", value=new, inline=False)
        emb.set_footer(
            text="Powered by tinyurl.com",
            icon_url="http://cr-api.com/static/img/branding/cr-api-logo.png",
        )
        await ctx.send(embed=emb)

    @commands.command(aliases=["urban"])
    async def ud(self, ctx, *, query):
        """Search terms with urbandictionary.com"""
        em = discord.Embed(title=f"{query}", color=discord.Color.green())
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        em.set_footer(text="Powered by urbandictionary.com")
        defs = ud.get_definition(query)
        try:
            res = defs[0]
        except IndexError:
            em.description = "No results."
            return await ctx.send(embed=em)
        em.description = f"**Definition:** {res.definition}\n**Usage:** {res.example}\n**Votes:** {res.upvotes}:thumbsup:{res.downvotes}:thumbsdown:"
        await ctx.send(embed=em)

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """!poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command()
    async def rate(self, ctx, *, thing: commands.clean_content):
        """Rates what you desire"""
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.send(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @commands.command()
    async def covid(self, ctx, *, country: str):
        """Covid-19 Statistics for any countries"""
        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())
        async with ctx.channel.typing():

            ref = await self.session.get(
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

            await ctx.send(
                f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
                embed=embed,
            )

    @commands.command()
    async def spoiler(self, ctx, *, query):
        await ctx.message.delete()
        await ctx.send(f"{ctx.message.author} sent a spoiler:\n||{query}|| ")

    @commands.command()
    async def strikethrough(self, ctx, *, query):
        await ctx.message.delete()
        await ctx.send(f"{ctx.message.author}:\n~~{query}~~ ")

    @commands.command(name="meme")
    @commands.cooldown(1, 2, BucketType.user)
    async def meme(self, ctx):
        """get a random meme from reddit!"""

        class MemeView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.ctx = ctx
            
            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                        await interaction.response.send_message("You didn't request the command", ephemeral=True)
                else:
                        return True

            @discord.ui.button(
                label="Next Meme", emoji="👏", style=discord.ButtonStyle.green
            )
            async def next_meme(
                self, button: discord.ui.Button, interaction: discord.Interaction
            ):
                await interaction.message.edit(embed=await generate_meme()) 

        await ctx.send(embed=await generate_meme(), view=MemeView())

    @commands.command(name="subreddit")
    @commands.cooldown(1, 2, BucketType.user)
    async def subreddit(self, ctx, *, subreddit):
        """get a random post from any subreddit"""
        subreddit = await self.reddit.subreddit(subreddit)
        all_subs = []
        async for submission in subreddit.hot(limit=20):
            if not submission.over_18:
                all_subs.append(submission)

        random_sub = random.choice(all_subs)
        name = random_sub.title
        url = random_sub.url
        em = discord.Embed(
            colour=discord.Colour.blurple(),
            title=name,
            url=f"https://reddit.com/{random_sub.id}",
        )
        if "comment" in url:
            url = random_sub.selftext
            em.description = url
        elif "v.redd.it" in url:
            em.description = url
        else:
            em.set_image(url=url)
        em.set_footer(
            text=f"Taken from r/{subreddit}, Score = {random_sub.score}, Upvote Ratio = {random_sub.upvote_ratio}"
        )
        await ctx.send(embed=em)

    @commands.command(name="wolfram", aliases=["ask"])
    async def _wolfram(self, ctx, *question: str):
        """Ask Wolfram Alpha any question."""
        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())
        api_key = os.getenv("WOLFRAM_API_KEY")
        if not api_key:
            return await ctx.send(
                "No API key set for Wolfram Alpha. Get one at http://products.wolframalpha.com/api/"
            )

        url = "http://api.wolframalpha.com/v2/query?"
        query = " ".join(question)
        payload = {"input": query, "appid": api_key}
        headers = {"user-agent": "spacebot"}
        async with ctx.typing():

            async with self.session.get(url, params=payload, headers=headers) as r:
                result = await r.text()
            root = ET.fromstring(result)
            a = []
            for pt in root.findall(".//plaintext"):
                if pt.text:
                    a.append(pt.text.capitalize())
        if len(a) < 1:
            message = "There is as yet insufficient data for a meaningful answer."
        else:
            message = "\n".join(a[0:3])
            if "Current geoip location" in message:
                message = "There is as yet insufficient data for a meaningful answer."

        await ctx.send(message)

    @commands.command(name="wolframimage")
    async def _image(self, ctx, *arguments: str):
        """Ask Wolfram Alpha any question. Returns an image."""
        if not arguments:
            return await ctx.send_help()
        api_key = os.getenv("WOLFRAM_API_KEY")
        if not api_key:
            return await ctx.send(
                "No API key set for Wolfram Alpha. Get one at http://products.wolframalpha.com/api/"
            )

        width = 800
        font_size = 30
        layout = "labelbar"
        background = "193555"
        foreground = "white"
        units = "metric"
        query = " ".join(arguments)
        query = urllib.parse.quote(query)
        url = f"http://api.wolframalpha.com/v1/simple?appid={api_key}&i={query}%3F&width={width}&fontsize={font_size}&layout={layout}&background={background}&foreground={foreground}&units={units}&ip=127.0.0.1"

        async with ctx.typing():

            async with self.session.request("GET", url) as r:
                img = await r.content.read()
                if len(img) == 43:
                    # img = b'Wolfram|Alpha did not understand your input'
                    return await ctx.send(
                        "There is as yet insufficient data for a meaningful answer."
                    )
                wolfram_img = io.BytesIO(img)
                try:
                    await ctx.channel.send(
                        file=discord.File(wolfram_img, f"wolfram{ctx.author.id}.png")
                    )
                except Exception as e:
                    await ctx.send(f"Oops, there was a problem: {e}")

    @commands.command(name="wolframsolve")
    async def _solve(self, ctx, *, query: str):
        """Ask Wolfram Alpha any math question. Returns step by step answers."""
        api_key = os.getenv("WOLFRAM_API_KEY")

        if not api_key:
            return await ctx.send(
                "No API key set for Wolfram Alpha. Get one at http://products.wolframalpha.com/api/"
            )

        url = f"http://api.wolframalpha.com/v2/query"
        params = {
            "appid": api_key,
            "input": query,
            "podstate": "Step-by-step solution",
            "format": "plaintext",
        }
        msg = ""

        async with ctx.typing():
            async with self.session.request("GET", url, params=params) as r:
                text = await r.content.read()
                root = ET.fromstring(text)
                for pod in root.findall(".//pod"):
                    if pod.attrib["title"] == "Number line":
                        continue
                    msg += f"{pod.attrib['title']}\n"
                    for pt in pod.findall(".//plaintext"):
                        if pt.text:
                            strip = pt.text.replace(" | ", " ").replace("| ", " ")
                            msg += f"- {strip}\n\n"
                if len(msg) < 1:
                    msg = "There is as yet insufficient data for a meaningful answer."
                await ctx.send(text)

    @commands.command(pass_context=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def convert(self, ctx, file_url, *, output_format):
        """Convert a video or audio file to anything you like
        correct output formats would be mp4, mp3, wav, that kind of stuff.
        Correct outputs can also be png, jpg, gif all that stuff.

        You can also get a copy of Rick Astley - Never gonna give you up by doing .convert rickrolled rick astley"""
        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())
        convertmsg = await ctx.send("Setting up...")
        # The copy of rickrolled part.
        if file_url == "rickrolled":
            file_url = "https://qoret.com/dl/uploads/2019/07/Rick_Astley_-_Never_Gonna_Give_You_Up_Qoret.com.mp3"
            meme = True
            number = "rickrolled_" + "".join(
                [random.choice("0123456789") for x in range(6)]
            )
            if output_format == "rick astley":
                input_format = "mp3"
                output_format = "mp4"

        else:
            meme = False
            number = "".join([random.choice("0123456789") for x in range(6)])
        if meme is False:
            form_found = False
            for i in range(6):
                if file_url[len(file_url) - i :].startswith("."):
                    input_format = file_url[len(file_url) - i :]
                    form_found = True
                else:
                    if form_found is not True:
                        form_found = False
            if form_found is not True:
                await convertmsg.edit(
                    "Your link is corrupt, it should end with something like .mp3, .mp4, .png, etc."
                )
                # print(form_found)
                return
        input = "{}.{}".format(number, input_format)
        output = "{}.{}".format(number, output_format)
        outputname = "{}.{}".format(number, output_format)
        await convertmsg.edit("Downloading...")
        try:

            async with self.session.get(file_url) as r:
                file = await r.content.read()
            with open(input, "wb") as f:
                f.write(file)
        except Exception as e:
            await convertmsg.edit("Could not download the file.")

            try:
                os.remove(input)
            except:
                pass
            return
        try:
            converter = ffmpy.FFmpeg(inputs={input: "-y"}, outputs={output: "-y"})
            await convertmsg.edit("Converting...")
            converter.run()
        except Exception as e:
            await convertmsg.edit("Could not convert your file, an error occured.")

            try:
                os.remove(input)
                os.remove(output)
            except:
                pass
            return
        await ctx.send(file=discord.File(output, outputname))
        await convertmsg.edit(
            f"File converted!!\nSuccessfully converted from {input_format} to {output_format}"
        )

        os.remove(input)
        os.remove(output)

    @checks.can_kick()
    @commands.command()
    async def embed(self, ctx, *, params):
        """Send complex rich embeds with this command!
        ```
        {description: Discord format supported}
        {title: required | url: optional}
        {author: required | icon: optional | url: optional}
        {image: image_url_here}
        {thumbnail: image_url_here}
        {field: required | value: required}
        {footer: footer_text_here | icon: optional}
        {timestamp} <-this will include a timestamp
        ```
        """
        em = await self.to_embed(ctx, params)
        await ctx.message.delete()
        try:
            await ctx.send(embed=em)
            self._last_embed = params
        except:
            await ctx.send("Improperly formatted embed!")

    @commands.command(pass_context=True)
    async def wiki(self, ctx, *, search: str = None):
        """Addictive Wikipedia results"""
        if search == None:
            await ctx.send(f"Usage: `{ctx.prefix}wiki [search terms]`")
            return

        results = wikipedia.search(search)
        if not len(results):
            no_results = await ctx.channel.send("Sorry, didn't find any result.")
            await asyncio.sleep(5)
            await ctx.message.delete(no_results)
            return

        newSearch = results[0]
        try:
            wik = wikipedia.page(newSearch)
        except wikipedia.DisambiguationError:
            more_details = await ctx.channel.send("Please input more details.")
            await asyncio.sleep(5)
            await ctx.message.delete(more_details)
            return

        emb = discord.Embed()
        emb.color = discord.Colour.random()
        emb.title = wik.title
        emb.url = wik.url
        textList = textwrap.wrap(
            wik.content, 500, break_long_words=True, replace_whitespace=False
        )
        emb.add_field(name="Wikipedia Results", value=textList[0] + "...")
        await ctx.send(embed=emb)

    async def to_embed(self, ctx, params):
        """Actually formats the parsed parameters into an Embed"""
        em = discord.Embed()

        if not params.count("{"):
            if not params.count("}"):
                em.description = params

        for field in self.get_parts(params):
            data = self.parse_field(field)

            color = data.get("color") or data.get("colour")
            if color == "random":
                em.color = random.randint(0, 0xFFFFFF)
            elif color == "chosen":
                maybe_col = discord.Colour.blue()
                if maybe_col:
                    raw = int(maybe_col.strip("#"), 16)
                    return discord.Color(value=raw)
                else:
                    return await ctx.send("Chosen color is not defined.")

            elif color:
                color = int(color.strip("#"), 16)
                em.color = discord.Color(color)

            if data.get("description"):
                em.description = data["description"]

            if data.get("desc"):
                em.description = data["desc"]

            if data.get("title"):
                em.title = data["title"]

            if data.get("url"):
                em.url = data["url"]

            author = data.get("author")
            icon, url = data.get("icon"), data.get("url")

            if author:
                em._author = {"name": author}
                if icon:
                    em._author["icon_url"] = icon
                if url:
                    em._author["url"] = url

            field, value = data.get("field"), data.get("value")
            inline = False if str(data.get("inline")).lower() == "false" else True
            if field and value:
                em.add_field(name=field, value=value, inline=inline)

            if data.get("thumbnail"):
                em._thumbnail = {"url": data["thumbnail"]}

            if data.get("image"):
                em._image = {"url": data["image"]}

            if data.get("footer"):
                em._footer = {"text": data.get("footer")}
                if data.get("icon"):
                    em._footer["icon_url"] = data.get("icon")

            if "timestamp" in data.keys() and len(data.keys()) == 1:
                em.timestamp = ctx.message.created_at

        return em

    def get_parts(self, string):
        """
        Splits the sections of the embed command
        """
        for i, char in enumerate(string):
            if char == "{":
                ret = ""
                while char != "}":
                    i += 1
                    char = string[i]
                    ret += char
                yield ret.rstrip("}")

    def parse_field(self, string):
        """
        Recursive function to get all the key val
        pairs in each section of the parsed embed command
        """
        ret = {}

        parts = string.split(":")
        key = parts[0].strip().lower()
        val = ":".join(parts[1:]).strip()

        ret[key] = val

        if "|" in string:
            string = string.split("|")
            for part in string:
                ret.update(self.parse_field(part))
        return ret

    @commands.group(invoke_without_command=True)
    async def lenny(self, ctx):
        """Lenny and tableflip group commands"""
        msg = "Available: `{}lenny face`, `{}lenny shrug`, `{}lenny tableflip`, `{}lenny unflip`"
        await ctx.send(msg.format(ctx.prefix))

    @lenny.command()
    async def shrug(self, ctx):
        """Shrugs!"""
        await ctx.send(content="¯\\\_(ツ)\_/¯")

    @lenny.command()
    async def tableflip(self, ctx):
        """Tableflip!"""
        await ctx.send(content="(╯°□°）╯︵ ┻━┻")

    @lenny.command()
    async def unflip(self, ctx):
        """Unfips!"""
        await ctx.send(content="┬─┬﻿ ノ( ゜-゜ノ)")

    @lenny.command()
    async def face(self, ctx):
        """Lenny Face!"""
        await ctx.send(content="( ͡° ͜ʖ ͡°)")

    @commands.command()
    async def ascii(self, ctx, *, text):
        async with self.session.get(
            f"http://artii.herokuapp.com/make?text={urllib.parse.quote_plus(text)}"
        ) as f:
            message = await f.text()
        if len("```" + message + "```") > 2000:
            await ctx.send("Your ASCII is too long!")
            return
        await ctx.send("```" + message + "```")

    @commands.command()
    async def whoisplaying(self, ctx, *, game):
        message = ""
        for member in ctx.guild.members:
            if member.activity != None:
                if member.activity.name == game:
                    message += str(member) + "\n"
        await ctx.send(
            embed=discord.Embed(
                title=f"Who is playing {game}?",
                description=message,
                color=discord.Colour.random(),
            )
        )

    @commands.command()
    async def maxfont(self, ctx, *, text):
        await asyncio.sleep(0.1)
        await ctx.send(text.replace("", " "))

    @commands.command(pass_context=True, aliases=["imgs"])
    async def imagesearch(self, ctx, *, query):
        """Google image search. [p]i Lillie pokemon sun and moon"""
        if query[0].isdigit():
            item = int(query[0])
            query = query[1:]
        else:
            item = 0
        async with self.session.get(
            "https://www.googleapis.com/customsearch/v1?q="
            + quote_plus(query)
            + "&start="
            + "1"
            + "&key="
            + os.getenv("GOOGLE_KEY")
            + "&cx="
            + os.getenv("GOOGLE_CX")
            + "&searchType=image"
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Google failed to respond.")
            else:
                result = json.loads(await resp.text())
                try:
                    result["items"]
                except:
                    return await ctx.send(
                        "There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine."
                    )
                if len(result["items"]) < 1:
                    return await ctx.send(
                        "There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine."
                    )
                em = discord.Embed()
                try:
                    em.set_image(url=result["items"][item]["link"])
                    show_search = True
                    if show_search:
                        em.set_footer(text='Search term: "' + query + '"')
                    await ctx.send(content=None, embed=em)
                except:
                    await ctx.send(result["items"][item]["link"])
                    await ctx.send('Search term: "' + query + '"')

    @commands.command(pass_context=True, aliases=["randim"])
    async def randomimage(self, ctx, *, query):
        """Get random images every time!"""
        if query[0].isdigit():
            item = int(query[0])
            query = query[1:]
        else:
            item = 0
        async with self.session.get(
            "https://www.googleapis.com/customsearch/v1?q="
            + quote_plus(query)
            + "&start="
            + "1"
            + "&key="
            + os.getenv("GOOGLE_KEY")
            + "&cx="
            + os.getenv("GOOGLE_CX")
            + "&searchType=image"
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Google failed to respond.")
            else:
                result = json.loads(await resp.text())
                try:
                    result["items"]
                except:
                    return await ctx.send(
                        "There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine."
                    )
                if len(result["items"]) < 1:
                    return await ctx.send(
                        "There were no results to your search. Use more common search query or make sure you have image search enabled for your custom search engine."
                    )
                em = discord.Embed()
                try:
                    n = random.randint(0, 10)
                    em.set_image(url=result["items"][n]["link"])
                    em.set_footer(text='Search term: "' + query + '"')
                    await ctx.send(content=None, embed=em)
                except Exception as e:
                    n = random.randint(0, 10)
                    await ctx.send(result["items"][n]["link"])
                    await ctx.send('Search term: "' + query + '"')

    @commands.command(aliases=["av"])
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await ctx.send(
            embed=discord.Embed(title=f"Avatar of {member.name}").set_image(
                url=member.avatar.url
            )
        )

    @commands.command()
    async def youtube(self, ctx, *, query: str):
        """Search YouTube"""

        html = urllib.request.urlopen(
            f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        )
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        await ctx.send(f"https://www.youtube.com/watch?v={video_ids[0]}")

    @commands.command()
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # take screenshot of a web page and send it to the channel
    async def screenshot(self, ctx, url: str):
        async with ctx.typing():
            # check if the url is not nsfw and valid
            # if not await self.is_nsfw(url) and ctx.channel.nsfw is False:
            #     return await ctx.send('This is not a NSFW channel.')

            await ctx.send(await self.screenshot_website(url))

    @commands.group()
    async def name(self, ctx):
        """Commands for NameGenerator."""

    @name.command()
    async def full(self, ctx: commands.Context, gender: str = None):
        """
        Generates a full name.
        Optional arguments:
        `gender`: Provides the gender of the name.
        """
        if gender:
            await ctx.send(full(gender=gender))
        else:
            await ctx.send(full())

    @name.command()
    async def first(self, ctx: commands.Context, gender: str = None):
        """
        Generates a first name.
        Optional arguments:
        `gender`: Provides the gender of the name.
        """
        if gender:
            await ctx.send(first(gender=gender))
        else:
            await ctx.send(first())

    @name.command()
    async def last(self, ctx: commands.Context):
        """
        Generates a last name.
        Optional arguments:
        `gender`: Provides the gender of the name.
        """
        await ctx.send(last())

    @name.command()
    async def mash(self, ctx, word1: str, word2: str):
        """
        Mash two words together.
        """
        a = word1
        b = word2
        await ctx.send(a[: len(a) // 2].strip() + b[len(b) // 2 :].strip())

    @commands.command()
    async def qr(self, ctx: commands.Context, *, text: str):
        """Create a QR code from text.

        When you scan this QR code, it will take you to google with the text query,
        or the website if you provide a website. That's essentially how QR codes work.
        """
        if len(text) > 250:
            await ctx.send("Please provide a sensible number of characters.")
            return

        qrc = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
        qrc.add_data(text)

        pred = lambda x: MessagePredicate.contained_in(list(map(str, range(1, x + 1))))
        await ctx.send(DEFAULT_OPENING_MESSAGE.format(text))

        try:
            result = await self.bot.wait_for("message", check=pred(3), timeout=100)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond, please start over.")
            return
        else:
            result = int(result.content)
            qrc_kwargs = {}
            embed_kwargs = {"color": 16777215}

            if result == 1:
                for shade in ("background", "fill"):
                    update = await self.get_colour_data(ctx, shade)
                    if update is False:
                        return
                    if shade == "background":
                        embed_kwargs["color"] = discord.Colour.from_rgb(
                            *update["back_color"]
                        )
                    qrc_kwargs.update(update)

            if result == 2:
                qrc_kwargs["image_factory"] = styledpil.StyledPilImage
                for style_type in ("drawers", "masks"):
                    update = await self.get_style_data(ctx, style_type)
                    if update is False:
                        return
                    qrc_kwargs.update(update)

        confirmation_message = await ctx.send("Generating QR code...")
        await ctx.trigger_typing()
        await asyncio.sleep(1)
        sender_kwargs = {}

        try:
            qrc = qrc.make_image(**qrc_kwargs)
        except DataOverflowError:
            sender_kwargs["content"] = "Failed to create a QR code for this text."
        else:
            buff = io.BytesIO()
            qrc.save(buff, "png")
            buff.seek(0)

            embed = discord.Embed(**embed_kwargs)
            embed.set_image(url="attachment://qr.png")
            embed.set_author(name="Generated QR code")
            embed.add_field(name="Content", value=text)
            sender_kwargs["embed"] = embed
            sender_kwargs["file"] = discord.File(buff, filename="qr.png")
        finally:
            try:
                await confirmation_message.edit(**sender_kwargs)
            except (discord.HTTPException, TypeError):
                # TypeError raised because of nonjsonserializable discord.File object
                await ctx.send(**sender_kwargs)

    @commands.command()
    async def download_reddit_video(self, ctx, videolink: str):
        """Downloads a reddit video"""
        await ctx.send("Downloading video...")
        await ctx.trigger_typing()
        if videolink.endswith("/"):
            videolink = videolink[:-1]

        if not videolink.endswith(".json"):
            videolink = videolink + ".json"

        async with aiohttp.ClientSession() as session:
            async with session.get(videolink) as resp:
                if resp.status != 200:
                    await ctx.send("Error: Video not found.")
                    return
                data = await resp.json()
        url = data[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"][
            "fallback_url"
        ]

        audio = url.replace("DASH_240.mp4", "DASH_audio.mp4")
        await ctx.send(audio)
        urllib.request.urlretrieve(audio, r".\utilities\photos\temp\audio.mp4")
        urllib.request.urlretrieve(url, r".\utilities\photos\temp\video.mp4")

        try:
            cmd = "ffmpeg -i ./utilities/photos/temp/video.mp4 -i ./utilities/photos/temp/audio.mp4 -c:v copy -c:a aac ./utilities/photos/temp/output.mp4"
            os.system(cmd)
            await ctx.send(
                "Your request has been queued. This will take 20 seconds. Chillax and enjoy."
            )
            await asyncio.sleep(20)
            await ctx.send(file=discord.File(r".\utilities\photos\temp\output.mp4"))
        except Exception as e:
            print(f"{e.__class__.__name__}:\n{e}")
            await ctx.send("Error: Failed to download video.")
            return


def setup(bot):
    bot.add_cog(Utility(bot))
