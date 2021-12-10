import discord
from discord.ext import commands
import sys
import traceback


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, "on_error"):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = commands.CommandNotFound

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"{ctx.command} has been disabled.")

        if isinstance(error, commands.errors.MissingRequiredArgument):
            return await ctx.send(f"{ctx.command} is missing required arguements")

        if isinstance(
            error, commands.errors.MissingPermissions or commands.errors.CheckFailure
        ):
            return await ctx.send(f"You are missing permissions to use this command")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if (
                ctx.command.qualified_name == "tag list"
            ):  # Check if the command being invoked is 'tag list'
                return await ctx.send("I could not find that member. Please try again.")

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
