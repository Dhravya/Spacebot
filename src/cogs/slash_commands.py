import re
import asyncio

import discord
from discord.commands import slash_command
from discord.ext import commands

import humor_langs
from googletrans import Translator
import urllib
from urllib.parse import quote_plus

from cogs.utility import generate_meme
from cogs.bot_commands import HelpOptions
from utilities.helpers.help import Help_Embed

translator = Translator()


class SlashCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.httpsession


    @slash_command()
    async def help(self,ctx):
        """Get help about the most feature packed bot!!"""
        view = HelpOptions(user=ctx.author, bot=self.bot)
        m = await ctx.respond(embed=Help_Embed(), view= view)
        await asyncio.sleep(60)
            # Disable all buttons 
        for button in view.children:
            button.disabled = True
        await m.edit_original_message(view=view)


    @slash_command()
    async def dev(self,ctx):
        """Get info about the developer of spacebot!"""
        em = discord.Embed(
            title="Contact the dev!!",
            description="Do you want a personalised bot for your server?\n Or make a website? Or do cool Machine learning stuff? \nWell, then [contact me!!](https://discord.com/channels/@me/512885190251642891)",
        )
        em.add_field(
            name="Website",
            value="[dhravya.me](https://dhravya.me)",
        )
        em.add_field(
            name="Twitter",
            value="[@dhravyashah](https://twitter.com/dhravyashah)",
            inline=False,
        )
        em.add_field(
            name="Github",
            value="[github/dhravya](https://github.com/dhravya)",
            inline=False,
        )
        em.add_field(
            name="Check out spacebot!",
            value="[Link to topgg page!](https://top.gg/bot/881862674051391499)\n[Link to website!](https://spacebot.ga)",
            inline=False,
        )
        em.colour = discord.Colour.blue()
        em.set_thumbnail(
            url="https://images-ext-2.discordapp.net/external/Ll2Us9DHwiMJ_et5L5J2_4QkfXMjQ0WB1w6EYb3G4wI/%3Fv%3D1/https/cdn.discordapp.com/emojis/856078862852161567.png"
        )
        await ctx.respond(embed=em)


    @slash_command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """gives info about member"""
        member = member or ctx.author
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
            value=f"<t:{int(member.created_at.timestamp())}:F>",
        )
        embed.add_field(
            name="Joined Server On:",
            value=f"<t:{int(member.joined_at.timestamp())}:F>",
        )

        embed.add_field(name="Roles:", value="".join([r.mention for r in member.roles[1:]]))
        embed.add_field(name="Highest Role:", value=member.top_role.mention)
        await ctx.respond(embed=embed)


    @slash_command()
    async def invite(self,ctx):
        """Invite spacebot to your server :)"""
        await ctx.resond("Invite spacebot now!! Use this link: https://dsc.gg/spacebt")


    @slash_command()
    async def kick(self,ctx, user: discord.Member):
        """Kicks a user from the server."""
        if not ctx.author.guild_permissions.kick_members == True:
            return await ctx.respond(
                "You dont have the permission to kick others -_-", ephemeral=True
            )
        if ctx.author == user:
            return await ctx.repond("You cannot kick yourself.", ephemeral=True)
        await user.kick()
        embed = discord.Embed(title=f"User {user.name} has been kicked.", color=0x00FF00)
        embed.add_field(name="Goodbye!", value=":boot:")
        try:
            embed.set_thumbnail(url=user.avatar.url)
        except:
            pass
        await ctx.respond(embed=embed)


    @slash_command()
    async def ban(self,ctx, user: discord.Member):
        """Bans a user from the server."""
        if not ctx.author.guild_permissions.ban_members == True:
            return await ctx.respond(
                "You dont have the permission to ban others -_-", ephemeral=True
            )
        if ctx.author == user:
            return await ctx.send("You cannot ban yourself.", ephemeral=True)
        await user.ban()
        embed = discord.Embed(title=f"User {user.name} has been banned.", color=0x00FF00)
        embed.add_field(name="Goodbye!", value=":hammer:")
        embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)


    @slash_command()
    async def mute(self,ctx, member: discord.Member, *, reason=None):
        """Mutes a user indefinitely"""
        if not ctx.author.guild_permissions.manage_messages == True:
            return await ctx.respond(
                "You dont have the permission to mute others -_-", ephemeral=True
            )

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



    @slash_command()
    async def unmute(self,ctx, user: discord.Member):
        """Unmutes a user."""

        if not ctx.author.guild_permissions.manage_messages == True:
            return await ctx.respond(
                "You dont have the permission to unmute others -_-", ephemeral=True
            )

        rolem = discord.utils.get(ctx.guild.roles, name="Muted")
        if rolem not in user.roles:
            return await ctx.respond("User is not muted.", ephemeral=True)
        embed = discord.Embed(title=f"User {user.name} has been unmuted.", color=0x00FF00)
        embed.add_field(name="Welcome back!", value=":open_mouth:")
        # embed.set_thumbnail(url= user.avatar.url)
        await ctx.send(embed=embed)
        await user.remove_roles(rolem)


    @slash_command()
    async def prune(self,ctx, count: int, member: discord.Member = None):
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


    @slash_command()
    async def clean(self,ctx):
        """Cleans the chat of the bot's messages."""
        if not ctx.author.guild_permissions.manage_messages == True:
            return await ctx.respond("You dont have the permission to delete messages -_-")

        def is_me(m):
            return m.author == self.bot.user

        await ctx.channel.purge(limit=100, check=is_me)


    @slash_command()
    async def announce(
        self, ctx, *, text: str, description: str, channel: discord.TextChannel = None
    ):
        """Sets an announcement to a particular channel. Please separate the title and description by a ,"""
        if not ctx.author.guild_permissions.manage_messages == True:
            return await ctx.respond("You dont have the permission to send messages -_-")
        if not channel:
            channel = ctx.channel
        # text = text.split(",")
        em = discord.Embed(
            title=text, description=description, colour=discord.Color.random()
        ).set_author(name=str(ctx.author.name), icon_url=str(ctx.author.avatar.url))
        await channel.send(embed=em)
        await ctx.respond("Announcement sent!!!")





    @slash_command()
    async def ascii(self,ctx, *, text: str):
        """Makes a fancy ascii art!"""
        async with self.bot.httpsession.get(
            f"https://api.dhravya.me/ascii?text={quote_plus(text)}&font=standard"
        ) as f:
            message = await f.text()
        if len("```" + message + "```") > 2000:
            await ctx.respond("Your ASCII is too long!")
            return
        await ctx.respond("```" + message + "```")



    @slash_command()
    async def tinyurl(self,ctx, link: str):
        """Compresses the size of url, powered by tinyurl"""
        url = "http://tinyurl.com/api-create.php?url=" + link

        async with self.bot.httpsession.get(url) as resp:
            new = await resp.text()
        emb = discord.Embed(color=discord.Colour.blurple())
        emb.add_field(name="Original Link", value=link, inline=False)
        emb.add_field(name="Shortened Link", value=new, inline=False)
        emb.set_footer(
            text="Powered by tinyurl.com",
            icon_url="http://cr-api.com/static/img/branding/cr-api-logo.png",
        )
        await ctx.respond(embed=emb)


    @slash_command()
    async def covidinfo(self,ctx, country: str):
        """Get stats about coronavirus in various countries!"""

        ref = await self.bot.httpsession.get(
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


    @slash_command()
    async def meme(self, ctx):
        """Gets a random meme from various subreddits"""

        class MemeView(discord.ui.View):
            def __init__(self):
                super().__init__()

            @discord.ui.button(
                label="Next Meme", emoji="👏", style=discord.ButtonStyle.green
            )
            async def next_meme(
                self, button: discord.ui.Button, interaction: discord.Interaction
            ):
                await interaction.message.edit(embed=await generate_meme())

        await ctx.send(embed=await generate_meme(), view=MemeView())


    @slash_command()
    async def cat(self,ctx):
        """Gets a random cute cat picture!"""
        emb = discord.Embed(color=discord.Colour.blurple())
        emb.set_image(url="https://api.dhravya.me/cat")
        await ctx.respond(embed=emb)



    @slash_command()
    async def dog(self,ctx):
        """Who doesnt like dogs?!"""

        emb = discord.Embed(color=discord.Colour.blurple())
        await ctx.respond(embed=emb.set_image(url="https://api.dhravya.me/dog"))


    @slash_command()
    async def owofy(self,ctx, *, text: str):
        """Converts your message in UwUs. its not worth trying, trust me."""
        await ctx.respond(
            f"<:uwupwease:896107914849296414> {humor_langs.owofy(text)} <:uwupwease:896107914849296414>"
        )


    @slash_command()
    async def ping(self, ctx):
        """Pong!"""
        await ctx.respond(f"Pong! {round(self.bot.latency * 1000)}ms")


    @slash_command()
    async def thank(
        self,
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


    @slash_command()
    async def youtube(self, ctx, *, query):

        html = urllib.request.urlopen(
            f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        )
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        await ctx.respond(f"https://www.youtube.com/watch?v={video_ids[0]}")



    @slash_command()
    async def translate(self,ctx,query):
        result = translator.translate(query)
        await ctx.respond(embed=discord.Embed(title=f"Translation",description=result.text).set_footer(text=f"{result.src} to {result.dest}"))



def setup(bot):
    bot.add_cog(SlashCommandCog(bot))