import asyncio, os
from py_compile import _get_default_invalidation_mode
from speedtest import Speedtest
from utilities.helpers import checks
import discord
from discord.ext import commands
from contextlib import suppress

from utilities.helpers.paginator import PageViewer


class CogNotFoundError(Exception):
    pass


class CogLoadError(Exception):
    pass


class NoSetupError(CogLoadError):
    pass


class CogUnloadError(Exception):
    pass


class OwnerUnloadWithoutReloadError(CogUnloadError):
    pass


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        em = discord.Embed()
        em.title = f"Error: {__name__}"
        em.description = f"{error}"
        em.color = 0xEE0000
        await ctx.send(embed=em)
        me =self.bot.get_user(881861601756577832)
        await me.send(embed=em)

    async def cog_before_invoke(self, ctx):
        """Check for bot owner"""
        if ctx.author.id == 881861601756577832:
            isOwner = True
        if not isOwner:
            raise commands.CommandInvokeError(
                "Only bot owner is permitted to use this command :man_technologist_tone1:"
            )
        return isOwner

    @checks.is_admin()
    @commands.command(name="speedtest", hidden=True)
    async def speed_test(self, ctx):
        """Speedtest"""
        async with ctx.typing():
            s = Speedtest()
            print("assigned")
            s.get_best_server()
            print("got server")
            s.download()
            print("calculated download")
            s.upload()
            print("calculated upload")
            s = s.results.dict()
            print("made dictionary")

            await ctx.send(
                f"Ping: `{s['ping']}ms`\nDownload: `{round(s['download']/10**6, 3)} Mbits/s`\nUpload: `{round(s['upload']/10**6, 3)} Mbits/s`\nServer: `{s['server']['sponsor']}, {s['server']['name']}, {s['server']['country']}`\nBot: `{s['client']['isp']}({s['client']['ip']}) {s['client']['country']} {s['client']['isprating']}`"
            )

    @commands.command(hidden=True)
    async def milestones(self, ctx):
        """Shows you in how many servers the bot is."""
        stats = await ctx.send("Getting stats, this may take a while.")

        uniquemembers = []
        servercount = len(self.bot.guilds)
        channelcount = len(list(self.bot.get_all_channels()))
        membercount = len(list(self.bot.get_all_members()))
        for member in list(self.bot.get_all_members()):
            if member.name not in uniquemembers:
                uniquemembers.append(member.name)
        uniquemembercount = len(uniquemembers)
        statsmsg = "I am currently in **{}** servers with **{}** channels, **{}** members of which **{}** unique.".format(
            servercount, channelcount, membercount, uniquemembercount
        )
        await stats.edit(statsmsg)
        # start of servercount milestones
        await asyncio.sleep(0.3)
        if servercount >= 10:
            statsmsg = statsmsg + "\n\n:white_check_mark: Reach 10 servers."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 10 servers."
        if servercount >= 50:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 50 servers."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 50 servers."
        if servercount >= 100:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 100 servers."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 100 servers."
        if servercount >= 500:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 500 servers."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 500 servers."
        if servercount >= 1000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 1000 servers."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 1000 servers."
        await stats.edit(statsmsg)
        # start of channelcount milestones
        await asyncio.sleep(0.3)
        if channelcount >= 10:
            statsmsg = statsmsg + "\n\n:white_check_mark: Reach 10 channels."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 10 channels."
        if channelcount >= 50:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 50 channels."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 50 channels."
        if channelcount >= 100:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 100 channels."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 100 channels."
        if channelcount >= 500:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 500 channels."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 500 channels."
        if channelcount >= 1000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 1000 channels."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 1000 channels."
        await stats.edit(statsmsg)
        # start of membercount milestones
        await asyncio.sleep(0.3)
        if membercount >= 1000:
            statsmsg = statsmsg + "\n\n:white_check_mark: Reach 1000 members."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 1000 members."
        if membercount >= 5000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 5000 members."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 5000 members."
        if membercount >= 10000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 10000 members."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 10000 members."
        if membercount >= 50000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 50000 members."
        else:
            statsmsg = statsmsg + "\n:negative_squared_cross_mark: Reach 50000 members."
        if membercount >= 100000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 100000 members."
        else:
            statsmsg = (
                statsmsg + "\n:negative_squared_cross_mark: Reach 100000 members.\n"
            )
        await stats.edit(statsmsg)
        # start of uniquemembercount milestones
        await asyncio.sleep(0.3)
        if uniquemembercount >= 1000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 1000 unique members."
        else:
            statsmsg = (
                statsmsg + "\n:negative_squared_cross_mark: Reach 1000 unique members."
            )
        if uniquemembercount >= 5000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 5000 unique members."
        else:
            statsmsg = (
                statsmsg + "\n:negative_squared_cross_mark: Reach 5000 unique members."
            )
        if uniquemembercount >= 10000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 10000 unique members."
        else:
            statsmsg = (
                statsmsg + "\n:negative_squared_cross_mark: Reach 10000 unique members."
            )
        if uniquemembercount >= 50000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 50000 unique members."
        else:
            statsmsg = (
                statsmsg + "\n:negative_squared_cross_mark: Reach 50000 unique members."
            )
        if uniquemembercount >= 100000:
            statsmsg = statsmsg + "\n:white_check_mark: Reach 100000 unique members."
        else:
            statsmsg = (
                statsmsg
                + "\n:negative_squared_cross_mark: Reach 100000 unique members."
            )
        await stats.edit(statsmsg)

    @commands.command(hidden=True)
    async def getguilds(self, ctx):
        if ctx.author.id == 881861601756577832:
            guild_list = []
            for guild in self.bot.guilds:
                guild_list.append(f"*{guild.name}* - `{guild.id}`")
            serverstring = ""
            embed_list = []
            # make an embed list with 50 guilds in each
            for i in range(0, len(guild_list), 25):
                embed = discord.Embed(title="Guilds", description="\n".join(guild_list[i:i + 50]))
                embed_list.append(embed)
                
            current_view = 0
            view = PageViewer(current_view, embed_list)
            await ctx.send(embed=embed_list[current_view],view=view)

    @commands.command()
    async def reload(self,ctx):
        msg = await ctx.send("Reloading cogs...")

        with suppress(discord.ExtensionNotLoaded):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    self.bot.unload_extension(f"cogs.{filename[:-3]}")

            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    self.bot.load_extension(f"cogs.{filename[:-3]}")

        await msg.edit(content=":success: | Cogs reloaded!")

    @commands.command(hidden=True)
    async def customstatusadd(self,ctx, *, status):
        await self.bot.wait_until_ready()
        if not ctx.message.author.id == 512885190251642891:
            return await ctx.send("this command isnt for you")
        self.bot.statuses.append(status)
        await ctx.send(f"Custom status {status} added")
        log_channel = self.bot.get_channel(893465721982562355)
        await log_channel.send(self.bot.statuses)


    @commands.command(hidden=True)
    async def customstatusremove(self,ctx, *, remove):
        await self.bot.wait_until_ready()
        if not ctx.message.author.id == 512885190251642891:
            return await ctx.send("this command isnt for you")
        try:
            self.bot.statuses.remove(remove)
            await ctx.send(f"Status `{remove}` removed!!")
        except:
            await ctx.send("There is no status with that name!")
        log_channel = self.bot.get_channel(893465721982562355)
        await log_channel.send(self.bot.statuses)

def setup(bot):
    bot.add_cog(Debug(bot))