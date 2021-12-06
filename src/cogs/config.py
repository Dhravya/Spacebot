import discord
from discord.ext import commands
from io import BytesIO
import copy

class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = bot.httpsession
        # Creating tables if they dont exist
        self.bot.dbcursor.execute("""CREATE TABLE IF NOT EXISTS 
                                        Servers(id int PRIMARY KEY                  NOT NULL, 
                                                levelon int                         DEFAULT 0, 
                                                fotd int                            , 
                                                qotd int                            , 
                                                level_channel int                   ,
                                                filtered_words VARCHAR(200)         DEFAULT "", 
                                                prefix VARCHAR(5)                   DEFAULT '.', 
                                                meme_channel int                    , 
                                                starboard_channel int               ,
                                                starboard_numberofRs int            , 
                                                welcome_message VARCHAR(2000) ,
                                                goodbye_message VARCHAR(2000) ,
                                                welcome_channel int ,
                                                welcome_toggle int DEFAULT 0,
                                                welcome_dm int DEFAULT 0,
                                                redditinfo VARCHAR(200))""")
                                                # TODO: Make use of these configs

        self.bot.dbcursor.execute("""CREATE TABLE IF NOT EXISTS
                                      Users(id int NOT NULL,
                                            guild_id int NOT NULL, 

                                            thank_count int DEFAULT 0,
                                            beer_count int DEFAULT 0,
                                            cringe_count int DEFAULT 0,
                                            hug_count int DEFAULT 0,
                                            f_count int DEFAULT 0,
                                            vote_reminder int DEFAULT 0,
                                            blacklisted int DEFAULT 0,
                                            last_voted TEXT,

                                            level int DEFAULT 0,
                                            experience int DEFAULT 0,

                                            FOREIGN KEY(guild_id) REFERENCES Servers(id))""")

        self.bot.dbcursor.execute("""CREATE TABLE IF NOT EXISTS 
                                        Roles(
                                            id int PRIMARY KEY NOT NULL,
                                            guild_id int NOT NULL,

                                            FOREIGN KEY(guild_id) REFERENCES Servers(id))""")

    # on error, send the error as an embed
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

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def wordcensor(self, ctx, *, word):
        """Censors a word on the server"""
        m = await ctx.send("...")
        try:
            self.bot.dbcursor.execute(
                f"SELECT filtered_words from Servers where id = {ctx.guild.id}")
            new_string = self.bot.dbcursor.fetchone()[0] + "%$" + word + "%$"
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
            self.bot.dbcursor.execute(
                f"SELECT filtered_words from Servers where id = {ctx.guild.id}")
            new_string = self.bot.dbcursor.fetchone()[0] + "%$" + word + "%$"
        self.bot.dbcursor.execute(
            f"UPDATE Servers SET filtered_words = '{new_string}' WHERE id = {ctx.guild.id}")
        self.bot.db.commit()
        await m.edit(content="Word added to the list of censored words")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def removecensor(self, ctx, *, word):
        """Remove censored words"""
        m = await ctx.send("...")
        try:
            previous_words = self.bot.dbcursor.execute(
                f"SELECT filtered_words from Servers where id = {ctx.guild.id}")
            
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO SERVERS(id) VALUES(?)",
                                      (ctx.guild.id,))
        new_string = previous_words.fetchone()[0].replace(
            "%$" + word + "%$", "")
        self.bot.dbcursor.execute(
            f"UPDATE Servers SET filtered_words = '{new_string}' WHERE id = {ctx.guild.id}")
        self.bot.db.commit()
        await m.edit(content="Word removed from the list of censored words")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def censoredwords(self, ctx):
        """Get the list of censored words of the server"""
        try:
            self.bot.dbcursor.execute(
                f"SELECT filtered_words from Servers where id = {ctx.guild.id}")
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
            self.bot.dbcursor.execute(F"SELECT filtered_words from Servers where id = {ctx.guild.id}")
        words = self.bot.dbcursor.fetchone()[0]
        words = words.split("%$")
        await ctx.send("\n".join(words))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def qotd(self, ctx, channel: discord.TextChannel = None):
        """Enables the question of the day to be sent to the respective channel
        This is a great way to keep the server active!"""
        if channel is None:
            channel = ctx.channel
        try:
            if self.bot.dbcursor.execute(f"SELECT qotd from Servers where id = {ctx.guild.id}").fetchone()[0] == channel.id:
                await ctx.send("QOTD is already enabled on this server!")
                return
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
            if self.bot.dbcursor.execute(f"SELECT qotd from Servers where id = {ctx.guild.id}").fetchone()[0] == channel.id:
                await ctx.send("QOTD is already enabled on this server!")
                return
        self.bot.dbcursor.execute(
            f"UPDATE Servers SET qotd = {channel.id} WHERE id = {ctx.guild.id}")
        self.bot.db.commit()
        await ctx.send("QOTD has been enabled on this server!")
        await channel.send("**Question of the day**\n\nWhat is your favourite colour? (SUCCESS!!! HAVE AN ACTIVE COMMUNITY!!)")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def fotd(self, ctx, channel: discord.TextChannel = None):
        """Enables the fact of the day to be sent to the respective channel
        This is a great way to keep the server active!"""
        if channel is None:
            channel = ctx.channel
        try:
            if self.bot.dbcursor.execute(f"SELECT fotd from Servers where id = {ctx.guild.id}").fetchone()[0] == channel.id:
                await ctx.send("FOTD is already enabled on this server!")
                return
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
            if self.bot.dbcursor.execute(f"SELECT fotd from Servers where id = {ctx.guild.id}").fetchone()[0] == channel.id:
                await ctx.send("FOTD is already enabled on this server!")
                return
        self.bot.dbcursor.execute(
            f"UPDATE Servers SET fotd = {channel.id} WHERE id = {ctx.guild.id}")
        self.bot.db.commit()
        await ctx.send("FOTD has been enabled on this server!")
        await channel.send("**Fact of the day**\n\n(SUCCESS!!! HAVE AN ACTIVE COMMUNITY!!)")

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def copyemoji(self, ctx, *, emoji: str):
        """Copy an emoji from another server to your own"""
        if len(ctx.message.guild.emojis) == 50:
            await ctx.message.delete()
            await ctx.send("Your Server has already hit the 50 Emoji Limit!")
            return
        emo_check = self.check_emojis(ctx.bot.emojis, emoji.split(":"))
        if emo_check[0]:
            emo = emo_check[1]
        else:
            emo = discord.utils.find(
                lambda e: emoji.replace(":", "") in e.name, ctx.bot.emojis
            )
        em = discord.Embed()
        em.color = discord.Colour.random()
        if emo == None:
            em.title = "Add Emoji"
            em.description = "Could not find emoji."
            await ctx.send(embed=em)
            return
        em.title = f"Added Emoji: {emo.name}"
        em.set_image(url="attachment://emoji.png")

        async with self.session.get(emo.url) as resp:
            image = await resp.read()
        with BytesIO(image) as file:
            await ctx.send(
                embed=em, file=discord.File(copy.deepcopy(file), "emoji.png")
            )
            await ctx.guild.create_custom_emoji(name=emo.name, image=file.read())

    def check_emojis(self, bot_emojis, emoji):
        for exist_emoji in bot_emojis:
            if emoji[0] == "<" or emoji[0] == "":
                if exist_emoji.name.lower() == emoji[1]:
                    return [True, exist_emoji]
            else:
                if exist_emoji.name.lower() == emoji[0]:
                    return [True, exist_emoji]
        return [False, None]

     # ensure that only administrators can use this command
    @commands.command()
    async def changeprefix(self, ctx, prefix):  # command: bl!changeprefix ...
        """Change the prefix of the bot"""
        if not ctx.author.id == 881861601756577832:
            if not ctx.author.guild_permissions.ban_members or not ctx.author.guild_permissions.administrator:
                await ctx.send("You do not have the permissions to do this!")
                return

        
        self.bot.dbcursor.execute("SELECT * FROM Servers WHERE id = ?", (ctx.guild.id,))
        if self.bot.dbcursor.fetchone() == None:
            self.bot.dbcursor.execute("INSERT INTO Servers(id, prefix) VALUES(?, ?)", (ctx.guild.id,prefix))
            self.bot.db.commit()
        else:
            self.bot.dbcursor.execute("UPDATE Servers SET prefix = ? WHERE id = ?", (prefix, ctx.guild.id))
            self.bot.db.commit()

        await ctx.send(f"Prefix changed to `{prefix}`!")


    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def memechannel(self, ctx):
        """Automatically adds reactions to memes in the channel"""
        await ctx.send("Here are all the commands for meme channel. ")

    @memechannel.command()
    @commands.has_permissions(manage_messages=True)
    async def set(self, ctx, channel: discord.TextChannel):
        """Set the channel for meme channel"""
        try:
            if self.bot.dbcursor.execute(f"SELECT meme_channel from Servers where id = {ctx.guild.id}").fetchone()[0] == channel.id:
                await ctx.send("Meme channel is already set to this channel!")
                return            
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
        self.bot.dbcursor.execute(f"UPDATE Servers SET meme_channel = {channel.id} WHERE id = {ctx.guild.id}")
        self.bot.db.commit()
        await ctx.send(f"Meme channel set to {channel.mention}")

    # @commands.command()
    # async def redditfeed_set(self, ctx, channel: discord.TextChannel):
    #     """Set the channel for reddit feed"""
    #     self.bot.dbcursor.execute(f"UPDATE Servers SET reddit_feed = {channel.id} WHERE id = {ctx.guild.id}")
    #     self.bot.db.commit()
    #     await ctx.send(f"Reddit feed channel set to {channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def starboard_set(self, ctx, channel: discord.TextChannel):
        """Set the channel for starboard"""

        try:
            if self.bot.dbcursor.execute(f"SELECT starboard_channel from Servers where id = {ctx.guild.id}").fetchone()[0] == channel.id:
                return await ctx.send("Starboard channel is already set to this one!")
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
        self.bot.dbcursor.execute(f"UPDATE Servers SET starboard_channel = {channel.id} WHERE id = {ctx.guild.id}")
        self.bot.db.commit()
        await ctx.send(f"Starboard channel set to {channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def welcome_setup(self, ctx):
        """Set the channel for welcome messages"""
        m = await ctx.send("Welcome to the welcome setup!! New joiners will be welcomed with a custom message in DM or channel or both. You can make it fancy!")
        try:
            if self.bot.dbcursor.execute(f"SELECT welcome_channel from Servers where id = {ctx.guild.id}").fetchone()[0] == ctx.channel.id:
                return await ctx.send("Welcome channel is already set to this one!")
        except TypeError:
            self.bot.dbcursor.execute("INSERT INTO Servers(id) VALUES(?)",
                                      (ctx.guild.id,))
        self.bot.dbcursor.execute(f"UPDATE Servers SET welcome_toggle = 1  WHERE id = {ctx.guild.id}")
        await ctx.send("Welcome has been turned on for this server")
        await ctx.send("Do you want to send the welcome message in a channel? Just type 'yes' or 'no'")
        setup1= await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if setup1.content.lower() == "no":
            self.bot.dbcursor.execute(f"UPDATE Servers SET welcome_channel = 0 WHERE id = {ctx.guild.id}")
            await ctx.send("Welcome channel has been turned off for this server")
        elif setup1.content.lower() == "yes":
            await ctx.send("Welcome channel is being set to this one. To change the settings, simply run the setup again in the correct channel, or just use the slash command (which makes things easier for both of us lol)")
            self.bot.dbcursor.execute(f"UPDATE Servers SET welcome_channel = {ctx.channel.id} WHERE id = {ctx.guild.id}")
            await ctx.send("Welcome channel has been set to " + ctx.channel.mention)
        else:
            await ctx.send("Please type 'yes' or 'no'")
            return

        await ctx.send("Do you want to send the welcome message in a DM? Just type 'yes' or 'no'")
        setup3 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if setup3.content.lower() == "yes":
            self.bot.dbcursor.execute(f"UPDATE Servers SET welcome_dm = 1 WHERE id = {ctx.guild.id}")
            await ctx.send("Welcome DM has been turned on for this server")
        elif setup3.content.lower() == "no":
            self.bot.dbcursor.execute(f"UPDATE Servers SET welcome_dm = 0 WHERE id = {ctx.guild.id}")
            await ctx.send("Welcome DM has been turned off for this server")
        else:
            await ctx.send("Please type 'yes' or 'no'")
            return

        self.bot.db.commit()
        await ctx.send("Welcome setup complete!!")

def setup(bot):
    bot.add_cog(Config(bot))
