import discord
from discord.ext import commands


class DiscordTogether(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
        await me.send(str(ctx.guild.id) ,embed=em)
    """Amazing Discord Multiplayer voice channel games!!!!!"""

    @commands.command()
    async def youtube_together(self, ctx):
        """Watch youtube together with your friends!"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'youtube')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command()
    async def chess(self, ctx):
        """Play a game of chess"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'chess')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command()
    async def poker(self, ctx):
        """Poker game """
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'poker')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command()
    async def betrayal_game(self, ctx):
        """Play with friends only to be betrayed"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'betrayal')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command()
    async def fishington(self, ctx):
        """Go fishing in fishington"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'fishing')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command()
    async def lettertile(self, ctx):
        """Play a game of scramble with friends!"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'letter-tile')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command()
    async def wordsnack(self, ctx):
        """IM too dumb for this lmfao"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'word-snack')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")

    @commands.command(aliases=["skribbl"])
    async def doodlecrew(self, ctx):
        """Play a game of scribbl with your friends!"""
        try:
            link = await self.bot.togetherControl.create_link(ctx.author.voice.channel.id, 'doodle-crew')
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play!")


def setup(bot):
    bot.add_cog(DiscordTogether(bot))
