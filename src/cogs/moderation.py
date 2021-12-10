import discord
from discord.ext import commands
from utilities.helpers import checks
from pytimeparse.timeparse import timeparse
import json


class Moderation(commands.Cog):
    """Commands for managing Discord servers."""

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
        me = self.bot.get_user(881861601756577832)
        await me.send(str(ctx.channel.id), embed=em)

    @checks.can_kick()
    @commands.command()
    async def kick(self, ctx, user: discord.Member):
        """Kicks a user from the server."""
        if ctx.author == user:
            return await ctx.send("You cannot kick yourself.")
        await user.kick()
        embed = discord.Embed(
            title=f"User {user.name} has been kicked.", color=0x00FF00
        )
        embed.add_field(name="Goodbye!", value=":boot:")
        embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)

    @checks.can_ban()
    @commands.command()
    async def ban(self, ctx, user: discord.Member):
        """Bans a user from the server."""
        if ctx.author == user:
            return await ctx.send("You cannot ban yourself.")
        await user.ban()
        embed = discord.Embed(
            title=f"User {user.name} has been banned.", color=0x00FF00
        )
        embed.add_field(name="Goodbye!", value=":hammer:")
        embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        guild = ctx.message.guild
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

    @checks.can_mute()
    @commands.command()
    async def unmute(self, ctx, user: discord.Member):
        """Unmutes a user."""
        rolem = discord.utils.get(ctx.guild.roles, name="Muted")
        if rolem not in user.roles:
            return await ctx.send("User is not muted.")
        embed = discord.Embed(
            title=f"User {user.name} has been unmuted.", color=0x00FF00
        )
        embed.add_field(name="Welcome back!", value=":open_mouth:")
        # embed.set_thumbnail(url= user.avatar.url)
        await ctx.send(embed=embed)
        await user.remove_roles(rolem)
        await self.bot.mongoIO.unmuteUser(user, ctx.guild)

    @checks.can_managemsg()
    @commands.command()
    async def prune(self, ctx, count: int):
        """Deletes a specified amount of messages. (Max 100)"""
        count = max(1, min(count, 100))
        await ctx.message.channel.purge(limit=count, bulk=True)

    @checks.can_managemsg()
    @commands.command()
    async def clean(self, ctx):
        """Cleans the chat of the bot's messages."""

        def is_me(m):
            return m.author == self.bot.user

        await ctx.message.channel.purge(limit=100, check=is_me)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a members and deletes their messages."""
        await member.ban(reason=f"Softban - {reason}")
        await member.unban(reason="Softban unban.")
        await ctx.send(f"Done. {member.name} was softbanned.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        """Warn a member via DMs"""
        warning = (
            f"You have been warned in **{ctx.guild}** by **{ctx.author}** for {reason}"
        )
        if not reason:
            warning = f"You have been warned in **{ctx.guild}** by **{ctx.author}**"
        try:
            await user.send(warning)
        except discord.Forbidden:
            return await ctx.send(
                "The user has disabled DMs for this guild or blocked the bot."
            )
        await ctx.send(f"**{user}** has been **warned**")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def announce(self, ctx, channel: discord.TextChannel = None, *, text=""):
        """Sets an announcement to a particular channel"""
        if not channel:
            channel = ctx.channel
        text = text.split(",")
        if len(text) != 2:
            return await ctx.send(
                "Please specify `,` separated two sentences- Title and description. :page_facing_up:"
            )
        em = discord.Embed(
            title=text[0], description=text[1], colour=discord.Color.random()
        ).set_author(name=str(ctx.author.name), icon_url=str(ctx.author.avatar.url))
        await channel.send(embed=em)
        await ctx.send("Announcement sent!!!")


def setup(bot):
    bot.add_cog(Moderation(bot))
