import discord
from discord.ext import commands
from io import BytesIO
import copy


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = bot.httpsession
        # Creating tables if they dont exist
        self.bot.dbcursor.execute(
            """CREATE TABLE IF NOT EXISTS 
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
                                                redditinfo VARCHAR(200))"""
        )
        # TODO: Make use of these configs

        self.bot.dbcursor.execute(
            """CREATE TABLE IF NOT EXISTS
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

                                            FOREIGN KEY(guild_id) REFERENCES Servers(id))"""
        )

        self.bot.dbcursor.execute(
            """CREATE TABLE IF NOT EXISTS 
                                        Roles(
                                            id int PRIMARY KEY NOT NULL,
                                            guild_id int NOT NULL,

                                            FOREIGN KEY(guild_id) REFERENCES Servers(id))"""
        )

    # on error, send the error as an embed
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
            if (
                not ctx.author.guild_permissions.ban_members
                or not ctx.author.guild_permissions.administrator
            ):
                await ctx.send("You do not have the permissions to do this!")
                return

        self.bot.dbcursor.execute("SELECT * FROM Servers WHERE id = ?", (ctx.guild.id,))
        if self.bot.dbcursor.fetchone() == None:
            self.bot.dbcursor.execute(
                "INSERT INTO Servers(id, prefix) VALUES(?, ?)", (ctx.guild.id, prefix)
            )
            self.bot.db.commit()
        else:
            self.bot.dbcursor.execute(
                "UPDATE Servers SET prefix = ? WHERE id = ?", (prefix, ctx.guild.id)
            )
            self.bot.db.commit()

        await ctx.send(f"Prefix changed to `{prefix}`!")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def memechannel(self, ctx):
        """Automatically adds reactions to memes in the channel"""
        await ctx.send("Use .help memechannel for more information.")

    @memechannel.command()
    @commands.has_permissions(manage_messages=True)
    async def set(self, ctx, channel: discord.TextChannel):
        """Set the channel for meme channel"""
        try:
            if (
                self.bot.dbcursor.execute(
                    f"SELECT meme_channel from Servers where id = {ctx.guild.id}"
                ).fetchone()[0]
                == channel.id
            ):
                await ctx.send("Meme channel is already set to this channel!")
                return
        except TypeError:
            self.bot.dbcursor.execute(
                "INSERT INTO Servers(id) VALUES(?)", (ctx.guild.id,)
            )
        self.bot.dbcursor.execute(
            f"UPDATE Servers SET meme_channel = {channel.id} WHERE id = {ctx.guild.id}"
        )
        self.bot.db.commit()
        await ctx.send(f"Meme channel set to {channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def starboard_set(self, ctx, channel: discord.TextChannel):
        """Set the channel for starboard"""

        try:
            if (
                self.bot.dbcursor.execute(
                    f"SELECT starboard_channel from Servers where id = {ctx.guild.id}"
                ).fetchone()[0]
                == channel.id
            ):
                return await ctx.send("Starboard channel is already set to this one!")
        except TypeError:
            self.bot.dbcursor.execute(
                "INSERT INTO Servers(id) VALUES(?)", (ctx.guild.id,)
            )
        self.bot.dbcursor.execute(
            f"UPDATE Servers SET starboard_channel = {channel.id} WHERE id = {ctx.guild.id}"
        )
        self.bot.db.commit()
        await ctx.send(f"Starboard channel set to {channel.mention}")

def setup(bot):
    bot.add_cog(Config(bot))
