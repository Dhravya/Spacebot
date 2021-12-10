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
        await me.send(str(ctx.channel.id) ,embed=em)
    """Amazing Discord Multiplayer voice channel games!!!!!"""

    @commands.command()
    async def youtube_together(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Watch youtube together with your friends!"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.watch_together, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")

    @commands.command()
    async def chess(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Play a game of chess"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.chess_in_the_park, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
            await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")

    @commands.command()
    async def poker(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Poker game """
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.poker_night, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
                        await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")


    @commands.command()
    async def betrayal_game(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Play with friends only to be betrayed"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.betrayal, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
                        await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")


    @commands.command()
    async def fishington(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Go fishing in fishington"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.fishington, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
                        await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")


    @commands.command()
    async def lettertile(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Play a game of scramble with friends!"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.letter_tile, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
                        await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")


    @commands.command()
    async def wordsnack(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """IM too dumb for this lmfao"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.word_snacks, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
                        await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")


    @commands.command(aliases=["skribbl"])
    async def doodlecrew(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Play a game of scribbl with your friends!"""
        if channel == None:
            channel = ctx.author.voice.channel
        try:
            link = await channel.create_activity_invite(discord.enums.EmbeddedActivity.doodle_crew, unique = False)
            await ctx.send(f"Click the blue link!\n{link}")
        except:
                        await ctx.send("You need to be in a voice channel to play! \nOr specify a voice channel")



def setup(bot):
    bot.add_cog(DiscordTogether(bot))
