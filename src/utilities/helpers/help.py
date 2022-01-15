from inspect import CO_VARARGS
import discord
from typing import List, Optional

def code_help_generator(bot:discord.ext.commands.Bot ,cog_name):
    """Generates the string with all command names with their description"""
    cog = bot.get_cog(cog_name)
    if cog is None:
        return f"{cog_name} is not a valid cog!"
    else:
        commands = cog.get_commands()
        if len(commands) == 0:
            return f"{cog_name} has no commands!"
        else:
            help_string = ""
            for command in commands:
                help_string += f"**{command.name}** - {command.help}\n"
            return help_string

def Help_Embed():
    em = discord.Embed(
        title="🔴 ***SPACEBOT HELP***",
        description=f"""
        > SpaceBot is an open source feature packed discord bot. Navigate the help menu to see all commands!
    
        Use @Spacebot help <command> to get more information about a command.

        [Invite](https://dsc.gg/spacebt) | [Spacebot is Open Source!](https://github.com/dhravya/spacebot)
        """,
    )
    em.set_image(
        url="https://images-ext-2.discordapp.net/external/MWmqAGeEWIpEaaq9rcMCrPYzMEScRGxEOB4ao9Ph2s0/https/media.discordapp.net/attachments/888798533459775491/903219469650890862/standard.gif"
    )
    em.set_footer(text="Join the Coding horizon now!!")
    # use custom colour
    em.colour = 0x2f3136
    return em
