import discord
from discord.ext import commands
from discord.ext import tasks
import random
from datetime import datetime
import re
from utilities.helpers.utils import VoteReminder, Votelink, Suicide

thank_words = "thanks|thank you|thank|ty"

class BackgroundTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.topggpy = bot.topggpy
        self.session = bot.httpsession
        self.reddit = bot.reddit

        self.do_fotd.start()
        self.do_qotd.start()
        self.update_stats.start()
        self.send_vote_reminder.start()

        self.meme_channel_list = None

    async def check_voted(self, userid):
        return await self.bot.topggpy.get_user_vote(userid)

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()
        name = message.author
        if message.author == self.bot.user:
            return

        # Suicide is no joke!!
        if (
            "kill myself" in message.content.lower()
            or "suicide" in message.content.lower()
        ):
            em = discord.Embed(
                colour=discord.Colour.dark_red(),
                title="Suicide is no joke!",
                description="""There are people who care for you... and suicide is not a solution for ANYTHING.
            \nPlease go to this website for suicide helpline. """,
                url="http://www.suicide.org",
            )
            em.set_image(
                url="https://media.discordapp.net/attachments/888801137568931881/901450078693240832/Screenshot_20211023-180951_Instagram.jpg?width=589&height=595"
            )
            await message.channel.send(embed=em, view=Suicide())

        self.bot.dbcursor.execute("SELECT meme_channel FROM Servers")
        ch = self.bot.dbcursor.fetchall()
        self.meme_channel_list = [x[0] for x in ch if x is not None]
        if message.channel.id in self.meme_channel_list and message.attachments:
            await message.add_reaction("<:upvote:881521766231584848>")
            await message.add_reaction("<:downvote:904068725475508274>")
            await message.add_reaction("😂")
            await message.add_reaction("😒")

        try:
            self.bot.dbcursor.execute(
                "SELECT thank_count from Users WHERE id = ?", (message.author.id,)
            )
        except KeyError:
            self.bot.dbcursor.execute(
                "INSERT INTO Users(id, guild_id) VALUES (?, ?)",
                (message.author.id, message.guild.id),
            )
            self.bot.db.commit()

        thank_search = re.search(thank_words, message.content.lower())
        if thank_search:
            if message.mentions:
                user = message.mentions[0]
                if user.bot:
                    return
                if user.id == message.author.id:
                    return await message.channel.send(
                        "You can't thank yourself, you know?"
                    )

                numbers = self.bot.dbcursor.execute(
                    "SELECT thank_count FROM Users WHERE id = ?", (user.id,)
                ).fetchone()
                print(numbers)
                if numbers is None:
                    self.bot.dbcursor.execute(
                        "INSERT INTO Users(id, guild_id) VALUES (?, ?)",
                        (user.id, message.guild.id),
                    )
                    self.bot.db.commit()
                    number = 0
                else:
                    number = numbers[0]
                self.bot.dbcursor.execute(
                    "UPDATE Users SET thank_count = ? WHERE id = ?",
                    (number + 1, user.id),
                )
                self.bot.db.commit()
                try:
                    await message.channel.send(
                        f"Added +1 Reputation to {user.mention}!"
                    )
                except:
                    pass

        if message.channel.id == 910789970514542662:
            data = message.content.split(" ")
            user = re.sub("\D", "", data[4])
            self.bot.dbcursor.execute("SELECT * from Users WHERE id = ?", (user,))
            user_data = self.bot.dbcursor.fetchone()
            if user_data is None:
                self.bot.dbcursor.execute(
                    "INSERT INTO Users(id, guild_id) VALUES (?, ?)",
                    (user, message.guild.id),
                )
                self.bot.db.commit()

            self.bot.dbcursor.execute(
                "UPDATE Users SET last_voted = ? WHERE id = ?",
                (str(datetime.now()), user),
            )
            user = self.bot.get_user(int(user))

            view = VoteReminder(self.bot, user)
            await user.send(
                embed=discord.Embed(
                    title="Thanks you for voting for Spacebot!!",
                    description="Your support is really appreciated!\nClick on the button below to be reminded every time you can vote!",
                ),
                view=view,
            )
            self.bot.dbcursor.execute("SELECT * from Users WHERE id = ?", (user.id,))
            user_data = self.bot.dbcursor.fetchone()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update the server count."""
        await self.bot.wait_until_ready()
        try:
            await self.bot.topggpy.post_guild_count()
            # chan = self.bot.get_channel(905906506464120872)
            # await chan.send(f"Posted server count ({self.bot.topggpy.guild_count})")
        except Exception as e:
            print(f"Failed to post server count\n{e.__class__.__name__}: {e}")

    @tasks.loop(seconds=30)
    async def do_qotd(self):
        await self.bot.wait_until_ready()

        dt = datetime.utcnow()

        if dt.hour == 12 and dt.minute == 5:
            truth_file = open(
                "utilities/text_data/truths.txt", mode="r", encoding="utf8"
            )
            truth_file_facts = truth_file.read().split("\n")
            truth_file.close()

            for i in truth_file_facts:
                if i == "":
                    truth_file_facts.remove(i)
            question = random.choice(truth_file_facts)
            em = discord.Embed(
                title="Question of the day!",
                description=question,
                colour=discord.Colour.blue(),
                timestamp=dt,
            )
            em.set_footer(text="Question of the day")
            self.bot.dbcursor.execute("SELECT DISTINCT qotd FROM Servers")
            qotd = self.bot.dbcursor.fetchall()
            qotd_channel_list = [x[0] for x in qotd]
            for channel in qotd_channel_list:
                if channel is not None:
                    channel = self.bot.get_channel(int(channel))
                    if channel is not None:
                        await channel.send(embed=em)

    @tasks.loop(seconds=30)
    async def do_fotd(self):
        """Sends the fact of the day to all the channels in the database"""
        await self.bot.wait_until_ready()
        dt = datetime.utcnow()

        if dt.hour == 12 and dt.minute == 5:
            truth_file = open(
                "utilities/text_data/facts.txt", mode="r", encoding="utf8"
            )
            truth_file_facts = truth_file.read().split("\n")
            truth_file.close()

            for i in truth_file_facts:
                if i == "":
                    truth_file_facts.remove(i)
            Fact = random.choice(truth_file_facts)
            em = discord.Embed(
                title="Fact of the day!",
                description=Fact,
                colour=discord.Colour.blue(),
                timestamp=dt,
            )
            em.set_footer(text="Fact of the day")
            self.bot.dbcursor.execute("SELECT DISTINCT fotd FROM Servers")
            fotd = self.bot.dbcursor.fetchall()
            fotd_channel_list = [x[0] for x in fotd]
            for channel in fotd_channel_list:
                if channel is not None:
                    channel = self.bot.get_channel(int(channel))
                    if channel is not None:
                        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.wait_until_ready()
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="Hi! I'm Spacebot!! 🥰",
                    description="Hey there! Thank you for adding me!\nMy prefix is `.`\nStart by typing `.help`\nTo use all my features, make sure to give me the following perms:\n~ `Manage Server`, `Kick`, `Ban`, `Manage emojis`, `Manage roles`, `Send messages`, `embed links`, `attach files`, `add reactions`, `use external emojis`, `manage messages`\nVoice channel: connect, speak.",
                    colour=discord.Colour.blue(),
                )
                return await channel.send(embed=embed)
        try:
            self.bot.dbcursor.execute(f"INSERT INTO Servers(id,) VALUES ({guild.id},)")
            self.bot.db.commit()
            print(f"Added server {guild.name} to database")
        except Exception as e:
            print("Failed to add server to database")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.wait_until_ready()
        self.bot.dbcursor.execute(f"DELETE FROM Servers WHERE id = {guild.id}")
        self.bot.db.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.bot.wait_until_ready()

        stars = ["⭐", "🌟"]
        if payload.emoji.name in stars:
            try:
                try:
                    self.bot.dbcursor.execute(
                        f"SELECT starboard_channel FROM Servers WHERE id = {payload.guild_id}"
                    )
                except:
                    self.bot.dbcursor.execute(
                        f"SELECT starboard_channel FROM Servers WHERE id = {payload.guild_id}"
                    )
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                reactions = discord.utils.get(
                    message.reactions, emoji=payload.emoji.name
                )
                if reactions.count == 4:
                    embed = discord.Embed(
                        title=f"🌟 New star 🌟",
                        description=message.content or ".",
                        colour=discord.Colour.blue(),
                        timestamp=message.created_at,
                    )
                    embed.add_field(name="JUMP TO THE MESSAGE!", value=message.jump_url)
                    if message.attachments:
                        attachment = message.attachments[0]
                        embed.set_image(url=attachment.url)
                    embed.set_footer(text=f"{message.author.name}'s message")
                    starboard_channel = self.bot.get_channel(
                        self.bot.dbcursor.fetchone()[0]
                    )
                    await starboard_channel.send(
                        f"New star in {channel.mention}", embed=embed
                    )
            except Exception as e:
                self.bot.console.print(
                    f"ERROR: Failed to post starboard message\n{e.__class__.__name__}: {e}",
                    style="error",
                )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.wait_until_ready()
        self.bot.dbcursor.execute(
            "SELECT id, welcome_channel, welcome_toggle, welcome_dm, welcome_message FROM Servers WHERE id = ?",
            (member.guild.id,),
        )
        result = self.bot.dbcursor.fetchone()
        if result is None:
            return
        if result[1] == 1:
            channel = self.bot.get_channel(result[0])
            if channel is not None:
                await channel.send(
                    f"{result[3]} <@{member.id}>"
                    if result[3]
                    else f"Welcome to {member.guild.name} {member.mention}"
                )
            if result[2] == 1:
                await member.send(
                    f"{result[3]} <@{member.id}>"
                    if result[3]
                    else f"Welcome to {member.guild.name} {member.mention}"
                )

    @tasks.loop(minutes=10)
    async def send_vote_reminder(self):
        await self.bot.wait_until_ready()
        self.bot.dbcursor.execute(f"SELECT id, vote_reminder, last_voted FROM Users")
        users = self.bot.dbcursor.fetchall()

        for user in users:
            if user[1] == 0:
                continue
            last_voted_datetime = user[2]
            last_voted_datetime = datetime.strptime(
                last_voted_datetime, "%Y-%m-%d %H:%M:%S.%f"
            )
            now = datetime.now()
            delta = now - last_voted_datetime
            # If delta is more than 12 hours then send reminder
            if 43800 > delta.total_seconds() > 43200:
                user_id = user[0]
                user = self.bot.get_user(user_id)
                if user is not None:
                    await user.send(
                        "Hey there! You haven't voted for Spacebot yet. Click this link in order to vote: https://top.gg/bot/881862674051391499/vote.",
                        view=Votelink,
                    )


def setup(bot):
    bot.add_cog(BackgroundTasks(bot))


#! ARCHIVED PART OF THE CODE
# @tasks.loop(minutes=2)

# async def do_reddit_feed(self):
#     await self.bot.wait_until_ready()

#     channels = channels_feed_list.keys()

#     for channel in channels:
#         channelid = int(channel)

#         id = db["servers"][str(self.bot.get_channel(channelid).guild.id)]["settings"][
#             "feeds"
#         ]["Last_reddit_post"][str(channelid)]
#         subredditname = channels_feed_list[channel]
#         subreddit = await self.reddit.subreddit(subredditname)
#         async for submission in subreddit.new(limit=1):
#             if not submission.over_18 and submission.id != id:
#                 name = submission.title
#                 url = submission.url

#                 em = discord.Embed(
#                     colour=discord.Colour.blurple(),
#                     title=name,
#                     url=f"https://reddit.com/{submission.id}",
#                 )
#                 if "comment" in url:
#                     url = submission.selftext
#                     em.description = url
#                 elif "v.redd.it" in url:
#                     em.description = url
#                     continue
#                 else:
#                     em.set_image(url=url)
#                 await subreddit.load()
#                 em.set_author(
#                     name=submission.author,
#                     icon_url="https://external-preview.redd.it/iDdntscPf-nfWKqzHRGFmhVxZm4hZgaKe5oyFws-yzA.png?auto=webp&s=38648ef0dc2c3fce76d5e1d8639234d8da0152b2",
#                 )
#                 em.set_footer(
#                     text=f"Taken from r/{subreddit}, Score = {submission.score}",
#                     icon_url=subreddit.icon_img,
#                 )

#                 target_channel = self.bot.get_channel(channelid)
#                 await target_channel.send(embed=em)
#                 db["servers"][str(self.bot.get_channel(channelid).guild.id)]["settings"][
#                     "feeds"
#                 ]["Last_reddit_post"][str(channelid)] = submission.id
#                 with open("otherfiles/data/db/database.json", "w") as f:
#                     json.dump(db, f, indent=4)
