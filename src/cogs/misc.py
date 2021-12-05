import discord
from discord.ext import commands
import random
from typing import Optional
from discord.ext import commands
from discord.ext.commands import Cog
import asyncio
import textwrap
import discord
from difflib import SequenceMatcher
from functools import partial
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands


prefix = "."
NASA_BASE_URL = "https://api.nasa.gov"
NASA_IMAGES_BASE_URL = "https://images-api.nasa.gov"
NASA_EPIC_BASE_URL = "https://epic.gsfc.nasa.gov"



class Misc(Cog):
    """Miscellaneous commands like space, discomegle and typeracer"""

    def __init__(self, bot):
        self._font = None
        self.http_session = bot.httpsession
        self.bot = bot

        self.pool = {}  # queue of users.id -> user channel
        self.link = {}  # userid -> {target id, target user channel}
        self.colour = 0xAAAAAA

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        em = discord.Embed()
        em.title = f"Error: {__name__}"
        em.description = f"{error}"
        em.color = 0xEE0000
        await ctx.send(embed=em)
        me =self.bot.get_user(881861601756577832)
        await me.send(str(ctx.guild.id) ,embed=em)

    async def get_quote(self) -> Tuple[str, str]:

        async with self.http_session.get("https://api.quotable.io/random") as resp:
            resp = await resp.json()
            return resp["content"], resp["author"]

    @property
    def font(self) -> ImageFont:
        if self._font is None:
            self._font = ImageFont.truetype(
                f"utilities/Menlo.ttf", encoding="unic"
            )
        return self._font

    def generate_image(self, text: str, color: discord.Color) -> discord.File:
        margin = 20
        newline = 10

        wrapped = textwrap.wrap(text, width=35)
        text = "\n".join(line.strip() for line in wrapped)

        img_width = self.font.getsize(max(wrapped, key=len))[0] + 2 * margin
        img_height = 20 * len(wrapped) + (len(wrapped) -
                                          1) * newline + 2 * margin

        with Image.new("RGBA", (img_width, img_height)) as im:
            draw = ImageDraw.Draw(im)
            draw.multiline_text(
                (margin, margin),
                text,
                spacing=newline,
                font=self.font,
                fill=color.to_rgb(),
            )

            buffer = BytesIO()
            im.save(buffer, "PNG")
            buffer.seek(0)

        return buffer

    async def render_typerace(self, text: str, color: discord.Color) -> discord.File:
        func = partial(self.generate_image, text, color)
        task = self.bot.loop.run_in_executor(None, func)
        try:
            return await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            raise commands.UserFeedbackCheckFailure(
                "An error occurred while generating this image. Try again later."
            )

    @commands.command(aliases=["tr"])
    @commands.cooldown(1, 10, commands.BucketType.guild)

    async def typerace(self, ctx: commands.Context) -> None:
        """
        Begin a typing race!
        Credits to Cats3153.
        """
        try:
            quote, author = await self.get_quote()
        except KeyError:
            raise commands.UserFeedbackCheckFailure(
                "Could not fetch quote. Please try again later."
            )

        color = discord.Color.random()
        img = await self.render_typerace(quote, color)
        embed = discord.Embed(color=color)
        embed.set_image(url="attachment://typerace.png")
        if author:
            embed.set_footer(text=f"~ {author}")

        m = await ctx.send("Race starts in ..")
        await m.edit("Race starts in 3 ..")
        await m.edit("Race starts in 3 2..")
        await m.edit("Race starts in 3 2 1..")
        msg = await ctx.send(file=discord.File(img, "typerace.png"), embed=embed)
        if ctx.author.typing():
            x = await ctx.send("Detected typing, timer starts")
        acc: Optional[float] = None

        def check(m: discord.Message) -> bool:
            if m.channel != ctx.channel or m.author.bot or not m.content:
                return False  # if satisfied, skip accuracy check and return
            content = " ".join(m.content.split())  # remove duplicate spaces
            accuracy = SequenceMatcher(None, quote, content).ratio()

            if accuracy >= 0.95:
                nonlocal acc
                acc = accuracy * 100
                return True
            return False

        ref = msg.to_reference(fail_if_not_exists=False)
        try:
            winner = await ctx.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                color=discord.Color.blurple(),
                description=f"No one typed the [sentence]({msg.jump_url}) in time.",
            )
            return await ctx.send(embed=embed, reference=ref)

        seconds = (winner.created_at - x.created_at).total_seconds()
        winner_ref = winner.to_reference(fail_if_not_exists=False)
        wpm = (len(quote) / 5) / (seconds / 60) * (acc / 100)
        description = (
            f"{winner.author.mention} typed the [sentence]({msg.jump_url}) in `{seconds:.2f}s` "
            f"with **{acc:.2f}%** accuracy. (**{wpm:.1f} WPM**)"
        )
        embed = discord.Embed(color=winner.author.color,
                              description=description)
        await ctx.send(embed=embed, reference=winner_ref)

    @commands.command(pass_context=True, no_pm=True)
    async def discomegle(self, ctx):
        """Chat with other discord people anonymously! DM THIS TO THE BOT"""
        user = ctx.message.author
        channel = ctx.message.channel
        try:
            server = user.guild
        except:
            pass
        msg = ""
        msg += "▸ **{}joinpool**: Joins the pool\n".format(prefix)
        msg += "▸ **{}next**: Changes partners\n".format(prefix)
        msg += "▸ **{}leavepool**: Leaves the pool or conversation\n".format(
            prefix)
        msg += "▸ **{}check**: Checks who's there\n".format(prefix)

        em = discord.Embed(description=msg, colour=user.colour)
        em.set_author(name="In a private message to this bot:")
        await ctx.send(embed=em)

    async def direct_message(self, message):
        msg = message.content
        user = message.author
        channel = message.channel
        if (
            channel is discord.ChannelType.private
            and not msg.startswith(prefix)
            and user.id in self.link
            and not message.guild
        ):
            target_channel = self.link[user.id]["TARGET_CHANNEL"]
            em = discord.Embed(description=msg, colour=self.colour)
            em.set_author(name="Partner")
            await target_channel.send(f"`Partner:` {msg}")

        else:
            if msg == (prefix + "joinpool"):
                await self.add_to_pool(message)
            elif msg == (prefix + "leavepool"):
                await self.remove_from_pool(message)
            elif msg == (prefix + "next"):
                await self.get_next_user(message)
            elif msg == (prefix + "check"):
                await self.get_info(message)

    async def add_to_pool(self, message):
        user = message.author
        channel = message.channel
        self.pool[user.id] = channel

        em = discord.Embed(
            description="**You have been added to the pool.**", colour=self.colour
        )
        await channel.send(embed=em)

    async def remove_from_pool(self, message):
        user = message.author
        channel = message.channel

        if user.id in self.pool.keys():
            self.pool.pop(user.id)
            em = discord.Embed(
                description="**Leaving discomegle pool.**", colour=self.colour
            )
            await channel.send(embed=em)
        elif user.id in self.link.keys():
            # put partner back into pool
            partner_id = self.link[user.id]["TARGET_ID"]
            partner_channel = self.link[user.id]["TARGET_CHANNEL"]
            self.pool[partner_id] = partner_channel
            self.link.pop(partner_id)
            self.link.pop(user.id)

            em = discord.Embed(
                description="**Your partner has disconnected.**", colour=self.colour
            )
            await partner_channel.send(embed=em)

            em = discord.Embed(
                description="**You have disconnected from the conversation.**",
                colour=self.colour,
            )
            await channel.send(embed=em)
        else:
            em = discord.Embed(
                description="**Leaving discomegle conversation and pool.**",
                colour=self.colour,
            )
            await channel.send(embed=em)

    # puts both users back in the pool, but will go to same person if pool is small
    async def get_next_user(self, message):
        user = message.author
        channel = message.channel

        if user.id in self.link.keys():
            # get partner information
            partner_id = self.link[user.id]["TARGET_ID"]
            partner_channel = self.link[user.id]["TARGET_CHANNEL"]
            self.pool[partner_id] = partner_channel
            self.pool[user.id] = channel

            self.link.pop(partner_id)
            self.link.pop(user.id)

            em = discord.Embed(
                description="**Your partner has disconnected.**", colour=self.colour
            )
            await partner_channel.send(embed=em)

            em = discord.Embed(
                description="**Switching Users.**", colour=self.colour)
            await channel.send(embed=em)

        elif user.id in self.pool.keys():
            em = discord.Embed(
                description="**You're still in the pool. Please wait.**",
                colour=self.colour,
            )
            await channel.send(embed=em)
        else:
            em = discord.Embed(
                description="**You are not in the pool. Please do `{}joinpool`.**",
                colour=self.colour,
            )
            await channel.send(embed=em)

    async def get_info(self, message):
        channel = message.channel

        msg = ""
        msg += "▸ Total Users: __{}__\n".format(
            len(self.pool) + len(self.link))
        msg += "▸ Users in conversation (should be even): __{}__\n".format(
            len(self.link)
        )
        msg += "▸ Unpaired users: __{}__".format(len(self.pool))

        em = discord.Embed(description=msg, colour=self.colour)
        await channel.send(embed=em)

    async def create_link(self):
        while self == self.bot.get_cog("Discomegle"):
            if len(self.pool) >= 2:
                # get two users
                user_one_id = random.choice(list(self.pool.keys()))
                user_one_channel = self.pool[user_one_id]
                self.pool.pop(user_one_id, None)

                user_two_id = random.choice(list(self.pool.keys()))
                user_two_channel = self.pool[user_two_id]
                self.pool.pop(user_two_id, None)

                self.link[user_one_id] = {
                    "TARGET_ID": user_two_id,
                    "TARGET_CHANNEL": user_two_channel,
                }
                self.link[user_two_id] = {
                    "TARGET_ID": user_one_id,
                    "TARGET_CHANNEL": user_one_channel,
                }

                em = discord.Embed(
                    description="**You have been paired. You can now start talking with your partner.**",
                    colour=self.colour,
                )
                await user_one_channel.send(embed=em)

                em = discord.Embed(
                    description="**You have been paired. You can now start talking with your partner.**",
                    colour=self.colour,
                )
                await user_two_channel.send(embed=em)

            await asyncio.sleep(5)


def setup(bot):
    n = Misc(bot)
    bot.add_listener(n.direct_message, "on_message")
    bot.loop.create_task(n.create_link())
    bot.add_cog(n)
