import discord
import time, datetime
from discord.ext import commands
from utilities.helpers.utils import Invite
from utilities.helpers.help import Help_Embed, code_help_generator
import asyncio


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional"
        self.set_footer(text=text)
        self.color = discord.Color.blurple()


class HelpOptions(discord.ui.View):
    def __init__(self, user, bot):
        super().__init__()
        self.user = user
        self.bot = bot
        self.add_item(
            discord.ui.Button(
                label="Join the Coding Horizon",
                url="https://dsc.gg/thecodinghorizon",
                row=2,
            )
        )
        self.add_item(
            discord.ui.Button(label="Meet the Developer", url="https://dhravya.me")
        )
        self.add_item(
            discord.ui.Button(label="Hosted on Epikhost", url="https://discord.gg/vTpkbk8Q64", row=2, emoji="<:epikhostlogo:859403955531939851>", style= discord.ButtonStyle.success)
        )
        self.add_item(
            discord.ui.Button(label="Privacy Policy", url="https://github.com/dhravya/spacebot/PRIVACY.md", row=1)
        )


    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️", row=3)
    async def delete_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.user:
            return await interaction.response.send_message("You didn't ask for the help command!", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.button(label="Back to home", style=discord.ButtonStyle.primary, emoji="🏠", row=3)
    async def back_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.user == self.user:
            return await interaction.response.send_message("You didn't ask for the help command!", ephemeral=True)
        view  = HelpOptions(user=interaction.user, bot=self.bot)
        await interaction.message.edit(embed=Help_Embed(), view=view)

    @discord.ui.select(
        placeholder="Select a Command Category",
        min_values=1,
        max_values=1,
        # One option for every cog
        # Generate a list of cog names with their values being the cog name
        options = [
            discord.SelectOption(
                label="Fun commands", value= "Fun", emoji="😂"
            ), 
            discord.SelectOption(
                label="Utility commands", value= "Utility", emoji="📦"
            ),
            discord.SelectOption(
                label="Music commands", value= "Music", emoji="🎵"
            ),
            discord.SelectOption(
                label="Moderation commands", value= "Moderation", emoji="🔨"
            ),
            discord.SelectOption(
                label="Bot Commands", value= "BotCommands", emoji="🤖"
            ),
            discord.SelectOption(
                label="Config", value= "Config", emoji="🔧"
            ),
            discord.SelectOption(
                label="Discord Together", value= "DiscordTogether", emoji="💬"
            ),
            discord.SelectOption(
                label="Button Roles", value= "ButtonRoles", emoji="🔘"
            ), 
            discord.SelectOption(
                label="Miscellaneous" , value="Misc", emoji="👀"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        if not interaction.user == self.user:
            return await interaction.response.send_message("You didn't ask for the help command!", ephemeral=True)

        if select.values[0]:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=f"{select.values[0]} Help!",
                    description=code_help_generator(bot=self.bot , cog_name= select.values[0]),
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

            view  = HelpOptions(user=ctx.author, bot=ctx.bot)
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
        self.startTime = bot.startTime
        self.bot = bot
        self.bot.help_command = MyHelpCommand()


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
        """Get the information about the developer with a lot of helpful links"""
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
        """Invite our bot to your server!"""
        await ctx.send(
            "***Add SpaceBot to your server now!*** https://dsc.gg/spacebt",
            view=Invite(),
        )

    @commands.command()
    async def suggestdev(self, ctx, *, suggestion):
        """Suggest a feature for the bot"""
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
        """Vote for SpaceBot on top.gg"""
        em = discord.Embed(
            title="Support Spacebot!😃🥰",
            description="Here's the vote link! https://top.gg/bot/881862674051391499/vote",
        )
        em.set_footer(text="Thanks for voting in advance :)")
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def nickscan(self, ctx):
        """Scan for nicknames"""
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

    @commands.command()
    async def privacy_policy(self,ctx):
        """Shows the privacy policy"""

        embed= discord.Embed(
            colour = 0x2f3136,
            title="Privacy Policy",
            description="""
            The use of this application ("Bot") in a server
             requires the collection of some specific user data ("Data"). 
             The Data collected includes, but is not limited to Discord user ID values. 
             Use of the Bot is considered an agreement to the terms of this Policy."""
        )
        embed.add_field(name="Access to data" , value= """
        Access to Data is only permitted to Bot's developers, 
        and only in the scope required for the development, testing, and implementation of features for Bot. 
        Data is not sold, provided to, or shared with any third party, except where required by law or a Terms of Service agreement. 
        You can view the data upon request from
        @Dhravya""", inline=False)
        embed.add_field(name="Storage of data" , value= """
        All data collected by the Bot is stored locally on an SQLITE database.
        The database is secured to prevent external access, 
        however no guarantee is provided and the Bot owners assume no liability for the unintentional or malicious breach of Data. 
        In the event of an unauthorised Data access, users will be notified through the Discord client application."""
        , inline=False)
        embed.add_field(name="User Rights" , value= """
        At any time, you have the right to request to view the Data pertaining to your Discord account. 
        You may submit a request by DMing [SpaceDoggo#0001](https://discord.com/channels/@me/512885190251642891). 
        You have the right to request the removal of relevant Data."""
        , inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="botinfo", aliases=["botstats", "status", "stats"])
    async def botstats(self, ctx):
        """Get statistics about the bot."""

        uptime = str(datetime.timedelta(seconds=int(round(time.time() - self.startTime))))
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
