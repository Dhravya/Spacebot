import discord
import time, datetime
from discord.ext import commands
from utilities.helpers.utils import Invite
from utilities.helpers.help import Help_Embed, cog_help
import asyncio


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional"
        self.set_footer(text=text)
        self.color = discord.Color.blurple()
        
def cog_help(cog):
    embed = discord.Embed(
        title=f"{cog} Commands", colour=discord.Color.random()
    )
    if cog.description:
        embed.description = cog.description

    for command in cog.get_commands():
        embed.add_field(
            name=command.qualified_name,
            value=f"{command.description}:" or "No Description:",
            inline=True,
        )

    return embed

class HelpOptions(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(
            discord.ui.Button(
                label="Join the server for chill and hangout!",
                url="https://dsc.gg/thecodinghorizon",
                row=1,
            )
        )
        self.add_item(
            discord.ui.Button(label="Developer", url="https://dhravya.me", row=1)
        )
        self.add_item(
            discord.ui.Button(label="Hosted on Epikhost", url="https://epikhost.xyz", row=1, emoji="<:epikhostlogo:859403955531939851>", style= discord.ButtonStyle.success)
        )


    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️", row=2)
    async def delete_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.user:
            return await interaction.response.send_message("You didn't ask for the help command!", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.select(
        placeholder="Select a Command Category",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Config", description="Configure your bot", emoji="🔧"
            ),
            discord.SelectOption(
                label="Music and Moderation commands",
                description="Music and moderation commands",
                emoji="🎶",
            ),
            discord.SelectOption(
                label="Utility",
                description="utilities like translate, convert, and more",
                emoji="⚙️",
            ),
            discord.SelectOption(
                label="Fun",
                description="This includes Fun Commands like AI and slap",
                emoji="🎠",
            ),
            discord.SelectOption(
                label="Games and Miscellaneous",
                description="Fun Games and Miscellaneous commands",
                emoji="🎭",
            ),
            discord.SelectOption(
                label="Bot Commands",
                description="Retrieves info about the user or the server",
                emoji="❓",
            ),
            discord.SelectOption(
                label="Image Commands",
                description="Image manipulation commands",
                emoji="📷",
            ),
        ],
    )
    async def select_callback(self, select, interaction):
        if not interaction.user == self.user:
            return await interaction.response.send_message("You didn't ask for the help command!", ephemeral=True)

        if select.values[0]:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=f"{select.values[0]} Help!",
                    description=cog_help,
                    colour=discord.Color.random(),
                ).set_footer(
                    text="Use `.help <command>` to get additional help on a specific command."
                )
            )


class MyHelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()

    async def send_pages(self):
        ctx = self.context

        try:

            view  = HelpOptions(user=ctx.author)
            m = await ctx.send(embed=Help_Embed(), view=view)
            await asyncio.sleep(60)
            for button in view.children:
                button.disabled = True
            await m.edit(view=view)

        except discord.Forbidden:
            await ctx.send(
                """Hey! it looks like i am missing some permissions. Please give me the following permissions:\n
                            - Send messages and embeds\n-Join and speak in voice channels\n-Ban, Kick and Delete messages\n thats it for the normal stuff... but remember... if i dont respond, its probably because i dont have the perms to do so."""
            )
    async def send_pages(self):
        ctx = self.context

        try:
            m = await ctx.send(embed=Help_Embed(), view=HelpOptions())
            await asyncio.sleep(120)
            try:
                await m.edit("This help session has expired", embed=Help_Embed(), view=None)
            except:
                pass
        except discord.Forbidden:
            await ctx.send(
                """Hey! it looks like i am missing some permissions. Please give me the following permissions:\n
                            - Send messages and embeds\n-Join and speak in voice channels\n-Ban, Kick and Delete messages\n thats it for the normal stuff... but remember... if i dont respond, its probably because i dont have the perms to do so."""
            )

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"{cog} Commands", colour=discord.Color.random()
        )
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(
                name=command.qualified_name,
                value=f"{command.description}:" or "No Description:",
                inline=True,
            )

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        embed = discord.Embed(title=command.qualified_name, colour=discord.Colour.random())
        embed.add_field(name="**Usage:**", value=self.get_command_signature(command))
        if command.description:
            embed.add_field(name="**Description:**", value=command.description, inline=True)
        if command.aliases:
            embed.add_field(name="**Aliases:**", value=", ".join([i for i in command.aliases]))

        # use of internals to get the cooldown of the command
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )
        await self.get_destination().send(embed=embed)
        
    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        ctx = self.context
        signature = self.get_command_signature(
            command
        )  # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(
            title=signature, description=command.help or "No help found..."
        )

        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)

        # use of internals to get the cooldown of the command
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )

        await ctx.send(embed=embed)


class BotCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.help_command = MyHelpCommand()
        global startTime
        startTime = time.time()

    @commands.Cog.listener()
    async def on_ready(self):

        print("yo done")

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

    @commands.command()
    async def dev(self, ctx):
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
            name="Check out spacebot",
            value="[Link to topgg page!](https://top.gg/bot/881862674051391499)\n[Link to website!](https://spacebot.ga)",
            inline=False,
        )
        em.colour = discord.Colour.blue()
        em.set_thumbnail(
            url="https://images-ext-2.discordapp.net/external/Ll2Us9DHwiMJ_et5L5J2_4QkfXMjQ0WB1w6EYb3G4wI/%3Fv%3D1/https/cdn.discordapp.com/emojis/856078862852161567.png"
        )
        await ctx.send(embed=em)

    @commands.command(description="Invite our bot to your server!")
    async def invite(self, ctx):

        await ctx.send(
            "***Add SpaceBot to your server now!*** https://dsc.gg/spacebt",
            view=Invite(),
        )

    @commands.command()
    async def suggestdev(self, ctx, *, suggestion):
        channel = self.bot.get_channel(924297401500577812)
        embed = discord.Embed(
            colour=discord.Color.blurple(),
            title=f"{ctx.author} Suggested:",
            description=suggestion,
        )
        await ctx.send("Suggestion sent to the devs, Thank you!", embed=embed)
        suggested = await channel.send(embed=embed)
        await suggested.add_reaction("👍")
        await suggested.add_reaction("👎")

    @commands.command()
    async def vote(self, ctx):
        em = discord.Embed(
            title="Support Spacebot!😃🥰",
            description="Here's the vote link! https://top.gg/bot/881862674051391499/vote",
        )
        em.set_footer(text="Thanks for voting in advance :)")
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def nickscan(self, ctx):
        message = "**Server | Nick**\n"
        for guild in self.bot.guilds:
            if guild.me.nick != None:
                message += f"{guild.name} | {guild.me.nick}\n"

        await ctx.send(
            embed=discord.Embed(
                title=f"Servers I Have Nicknames In",
                description=message,
                color=discord.Colour.random(),
            )
        )

    @commands.command(name="botinfo", aliases=["botstats", "status", "stats"])
    async def botstats(self, ctx):
        """Bot stats."""

        uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))
        # Embed
        em = discord.Embed(color=0x4FFCFA)
        em.set_author(name=f"{self.bot.user} Stats:", icon_url=self.bot.user.avatar.url)
        em.add_field(name=":crossed_swords: Servers", value=f"`{len(self.bot.guilds)}`")
        em.add_field(name="uptime", value=uptime)
        em.add_field(
            name="Ping", value=f"{round(self.bot.latency * 1000)}ms :white_check_mark:"
        )
        em.add_field(
            name="Member Count", value=f"{len(list(self.bot.get_all_members()))}"
        )

        topstats = await self.bot.topggpy.get_bot_info(881862674051391499)
        em.add_field(name="Top GG total votes", value=f'{topstats["points"]}')
        em.add_field(name="Top GG Monthly votes", value=f"{topstats['monthly_points']}")

        try:
            await ctx.send(embed=em)
        except Exception:
            await ctx.send(
                "I don't have permission to send embeds here :disappointed_relieved:"
            )

    @commands.command()
    async def ping(self, ctx):
        """checks ping and latency"""
        await ctx.send(
            f"🟢 Pong! My ping currently is {round(self.bot.latency * 1000)}ms :white_check_mark:"
        )

    @commands.command()
    async def pingtime(self, ctx: commands.Context):
        """Ping pong."""

        # https://github.com/aikaterna/aikaterna-cogs/blob/v3/pingtime/pingtime.py
        msg = "Pong!\n"
        for shard, ping in ctx.bot.latencies:
            msg += f"Shard {shard+1}/{len(ctx.bot.latencies)}: {round(ping * 1000)}ms\n"
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(BotCommands(bot))
