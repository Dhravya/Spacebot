import discord
import aiosqlite
from discord.commands import slash_command
from discord.ext import commands

# Courtesy of Pycord examples
"""
Let users assign themselves roles by clicking on Buttons.
The view made is persistent, so it will work even when the bot restarts.
See this example for more information about persistent views
https://github.com/Pycord-Development/pycord/blob/master/examples/views/persistent.py
Make sure to load this cog when your bot starts!
"""


class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        super().__init__(label=role.name,
                         style=discord.enums.ButtonStyle.primary, custom_id=str(role.id))

    async def callback(self, interaction: discord.Interaction):
        """This function will be called any time a user clicks on this button
        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that was created when the user clicked on the button
        """

        # figure out who clicked the button
        user = interaction.user
        # get the role this button is for (stored in the custom ID)
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            # if this role doesn't exist, ignore
            # you can do some error handling here
            return

        # passed all checks
        # add the role and send a response to the uesr ephemerally (hidden to other users)
        if role not in user.roles:
            # give the user the role if they don't already have it
            await user.add_roles(role)
            await interaction.response.send_message(f"🎉 You have been given the role {role.mention}", ephemeral=True)
        else:
            # else, take the role from the user
            await user.remove_roles(role)
            await interaction.response.send_message(f"❌ The {role.mention} role has been taken from you", ephemeral=True)


class ButtonRoleCog(commands.Cog):
    """A cog with a slash command for posting the message with buttons
    and to initialize the view again when the bot is restarted
    """

    def __init__(self, bot):
        self.bot = bot

    # make sure to set the guild ID here to whatever server you want the buttons in
    @slash_command(name="reactionrole")
    async def reactionrole(self, ctx, channel: discord.TextChannel, title: str, description: str, role1: discord.Role, role2: discord.Role = None, role3: discord.Role = None):
        """Slash command to post a new view with a button for each role
        """

        if not ctx.author.guild_permissions.manage_roles == True:
            return await ctx.respond("You dont have the permission to manage roles -_-")

        # timeout is None because we want this view to be persistent
        view = discord.ui.View(timeout=None)
        role_ids = [role1.id]
        if role2 is not None:
            role_ids.append(role2.id)
        if role3 is not None:
            role_ids.append(role3.id)

        # loop through the list of roles and add a new button to the view for each role
        for role_id in role_ids:
            # get the role the guild by ID
            try:
                await self.bot.db.execute("INSERT INTO Roles(id , guild_id) VALUES (? ,?)", (role_id, ctx.guild.id))
            except aiosqlite.IntegrityError:
                return await ctx.respond("A Button role with the same thing already exists.\n In order to cancel that role, just use the command /reactionrole_remove <roleid>")

            self.bot.db.commit()
            role = ctx.guild.get_role(role_id)
            view.add_item(RoleButton(role))
        await ctx.respond("success", ephemeral=True)
        await channel.send(embed=discord.Embed(title=title, description=description, colour=discord.Colour.random()), view=view)

    @slash_command(name="rr_remove")
    async def reactionrole_remove(self, ctx, role: discord.Role):
        """Slash command to remove a role button
        """
        if not ctx.author.guild_permissions.manage_roles == True:
            return await ctx.respond("You dont have the permission to manage roles -_-")
        try:
            self.bot.db.execute("DELETE FROM Roles WHERE id = ?", (role.id,))
            self.bot.db.commit()
            await ctx.respond("Successfully removed the role button")
        except aiosqlite.IntegrityError:
            await ctx.respond("A Button role with the same thing already exists.\n In order to cancel that role, just use the command /reactionrole_remove <roleid>")

    @commands.Cog.listener()
    async def on_ready(self):
        """This function is called every time the bot restarts.
        If a view was already created before (with the same custom IDs for buttons)
        it will be loaded and the bot will start watching for button clicks again.
        """

        # we recreate the view as we did in the /post command
        view = discord.ui.View(timeout=None)
        role = self.bot.db.execute("SELECT * FROM Roles")

        # make a list of guilds and roles of that guild
        for row in role:
            role = self.bot.get_guild(row[1]).get_role(row[0])
            view.add_item(RoleButton(role))

        # add the view to the bot so it will watch for button interactions
        self.bot.add_view(view)


def setup(bot):
    # load the cog
    bot.add_cog(ButtonRoleCog(bot))
