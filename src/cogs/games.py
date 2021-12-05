import discord
from discord.ext import commands
import asyncio
import itertools
import random
from typing import List
from utilities.games import twenty, hangman


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = "X won!"
            elif winner == view.O:
                content = "O won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + \
                self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class Games(commands.Cog):
    """Games like Chess, Connect4- ALL ON DISCORD!!"""

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
        await me.send(embed=em)

    @commands.command(name="connect4")
    async def connect4(self, ctx: commands.Context, opponent="", width=7, height=6):
        """Connect4 for the boredom"""
        # -------------- Help section ------------------#
        if opponent == "":
            em = discord.Embed()
            em.title = f"Usage: .connect4 opponent [width] [height]"
            em.description = f"Challenges opponent to a game of connect 4. The Opponent should be @mentoned to start\nBoard is default 7x6 large if not specified, though you usually wont need any board larger than that.\nMax board volume is 95 due to character limitations"
            em.add_field(
                name="Example",
                value=".connect4 @Username\n/connect4 @Username 10 9",
                inline=False,
            )
            em.color = 0x22BBFF
            await ctx.send(embed=em)
            return
        # ----------------------------------------------#
        # Remove challenge message
        await ctx.channel.delete_messages(await self.getMessages(ctx, 1))

        # Game init
        resized = False
        if width * height > 95:
            width = 7
            height = 6
            resized = True
        player1 = ctx.message.mentions[0].name
        player2 = ctx.message.author.name
        s = ":black_large_square:"
        p1 = ":blue_circle:"
        p2 = ":red_circle:"
        board = []
        for column in range(height):
            rowArr = []
            for row in range(width):
                rowArr.append(s)
            board.append(rowArr)

        def getDisplay():
            toDisplay = ""
            for y in range(height):
                for x in range(width - 1):
                    toDisplay += board[y][x] + "|"
                toDisplay += board[y][width - 1] + "\n"
            return toDisplay

        boardMessage = None
        em = discord.Embed()
        if player1 == player2:
            em.title = f"{player2} challenged themselves to a game of Connect 4 \n(wow you're lonely)"
        else:
            em.title = f"{player2} challenged {player1} to a game of Connect 4"
        em.description = f"{getDisplay()}"
        em.color = 0x444444
        em.add_field(
            name=f"{player1}",
            value=f"Type a number from 1-{width} to accept and place your first piece, or type 'decline' to refuse",
            inline=False,
        )
        if resized:
            em.add_field(
                name="Note",
                value=f"Original board length was too large, defaulted to 7x6",
                inline=False,
            )
        await ctx.send(embed=em)
        async for x in ctx.channel.history(limit=1):
            boardMessage = x
        badInput = 0
        turns = 1
        currentPlayer = player1
        otherPlayer = player2
        currentPlayerId = 1
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author.name == player1,
                    timeout=30,
                )
                if msg.content == "decline":
                    em = discord.Embed()
                    if player1 == player2:
                        em.title = f"{player2} challenged themselves to a game of Connect 4 (wow you're lonely)"
                    else:
                        em.title = (
                            f"{player2} challenged {player1} to a game of Connect 4"
                        )
                    em.description = f"{getDisplay()}"
                    em.color = 0x444444
                    em.add_field(
                        name=f"{player1}", value="Challenge refused", inline=False
                    )
                    await boardMessage.edit(embed=em)
                    return

                slot = int(msg.content)
                if slot < 1 or slot > width:
                    raise ValueError
                await ctx.channel.delete_messages(await self.getMessages(ctx, 1))
                board[height - 1][slot - 1] = p1
                gameLoop = True
                currentPlayer = player2
                otherPlayer = player1
                turns += 1
                currentPlayerId = 2
                break
            except asyncio.exceptions.TimeoutError:
                em = discord.Embed()
                if player1 == player2:
                    em.title = f"{player2} challenged themselves to a game of Connect 4 (wow you're lonely)"
                else:
                    em.title = f"{player2} challenged {player1} to a game of Connect 4"
                em.description = f"{getDisplay()}"
                em.color = 0x444444
                em.add_field(name=f"{player1}",
                             value="Game timed out", inline=False)
                await boardMessage.edit(embed=em)
                return
            except ValueError:
                em = discord.Embed()
                if player1 == player2:
                    em.title = f"{player2} challenged themselves to a game of Connect 4 (wow you're lonely)"
                else:
                    em.title = f"{player2} challenged {player1} to a game of Connect 4"
                em.description = f"{getDisplay()}"
                em.color = 0x444444
                em.add_field(
                    name=f"{player1}",
                    value=f"Enter a valid number from 1-{width}",
                    inline=False,
                )
                await boardMessage.edit(embed=em)
                badInput += 1
            if badInput == 3:
                em = discord.Embed()
                if player1 == player2:
                    em.title = f"{player2} challenged themselves to a game of Connect 4 (wow you're lonely)"
                else:
                    em.title = f"{player2} challenged {player1} to a game of Connect 4"
                em.description = f"{getDisplay()}"
                em.color = 0x444444
                em.add_field(
                    name=f"{player1}",
                    value="Did not enter a valid number in 3 tries. Game ended.",
                    inline=False,
                )
                await boardMessage.edit(embed=em)
                return
        winningComment = ""
        winner = ""
        while gameLoop:
            if turns == width * height:
                winner = None
                break
            ################################
            # check for winning combinations#
            ################################
            # Horizontal
            for y in range(height):
                for x in range(width - 3):
                    if (
                        board[y][x] == board[y][x + 1]
                        and board[y][x] == board[y][x + 2]
                        and board[y][x] == board[y][x + 3]
                        and board[y][x] != s
                    ):
                        if board[y][x] == p1:
                            board[y][x] = ":large_blue_diamond:"
                            board[y][x + 1] = ":large_blue_diamond:"
                            board[y][x + 2] = ":large_blue_diamond:"
                            board[y][x + 3] = ":large_blue_diamond:"
                        elif board[y][x] == p2:
                            board[y][x] = ":diamonds:"
                            board[y][x + 1] = ":diamonds:"
                            board[y][x + 2] = ":diamonds:"
                            board[y][x + 3] = ":diamonds:"
                        print("winner")
                        winner = otherPlayer
                        winningComment = (
                            f"{otherPlayer} connected 4 in a horizontal row"
                        )
                        break
                if winner != "":
                    break
            # Vertical
            for y in range(height - 3):
                for x in range(width):
                    if (
                        board[y][x] == board[y + 1][x]
                        and board[y][x] == board[y + 2][x]
                        and board[y][x] == board[y + 3][x]
                        and board[y][x] != s
                    ):
                        if board[y][x] == p1:
                            board[y][x] = ":large_blue_diamond:"
                            board[y + 1][x] = ":large_blue_diamond:"
                            board[y + 2][x] = ":large_blue_diamond:"
                            board[y + 3][x] = ":large_blue_diamond:"
                        elif board[y][x] == p2:
                            board[y][x] = ":diamonds:"
                            board[y + 1][x] = ":diamonds:"
                            board[y + 2][x] = ":diamonds:"
                            board[y + 3][x] = ":diamonds:"
                        winner = otherPlayer
                        winningComment = f"{otherPlayer} connected 4 in a vertical row"
                        break
                if winner != "":
                    break
            # diagonal \
            for y in range(height - 3):
                for x in range(width - 3):
                    if (
                        board[y][x] == board[y + 1][x + 1]
                        and board[y][x] == board[y + 2][x + 2]
                        and board[y][x] == board[y + 3][x + 3]
                        and board[y][x] != s
                    ):
                        if board[y][x] == p1:
                            board[y][x] = ":large_blue_diamond:"
                            board[y + 1][x + 1] = ":large_blue_diamond:"
                            board[y + 2][x + 2] = ":large_blue_diamond:"
                            board[y + 3][x + 3] = ":large_blue_diamond:"
                        elif board[y][x] == p2:
                            board[y][x] = ":diamonds:"
                            board[y + 1][x + 1] = ":diamonds:"
                            board[y + 2][x + 2] = ":diamonds:"
                            board[y + 3][x + 3] = ":diamonds:"
                        winner = otherPlayer
                        winningComment = f"{otherPlayer} connected 4 in a \ diagonal"
                        break
                if winner != "":
                    break
            # diagonal /
            for y in range(height - 3):
                for x in range(3, width):
                    if (
                        board[y][x] == board[y + 1][x - 1]
                        and board[y][x] == board[y + 2][x - 2]
                        and board[y][x] == board[y + 3][x - 3]
                        and board[y][x] != s
                    ):
                        if board[y][x] == p1:
                            board[y][x] = ":large_blue_diamond:"
                            board[y + 1][x - 1] = ":large_blue_diamond:"
                            board[y + 2][x - 2] = ":large_blue_diamond:"
                            board[y + 3][x - 3] = ":large_blue_diamond:"
                        elif board[y][x] == p2:
                            board[y][x] = ":diamonds:"
                            board[y + 1][x - 1] = ":diamonds:"
                            board[y + 2][x - 2] = ":diamonds:"
                            board[y + 3][x - 3] = ":diamonds:"
                        winner = otherPlayer
                        winningComment = f"{otherPlayer} connected 4 in a / diagonal"
                        break
                if winner != "":
                    break
            if winner != "":
                break
            ################################
            em = discord.Embed()
            em.title = f"Connect 4"
            em.description = f"{getDisplay()}"
            em.color = 0x444444
            em.add_field(
                name=f"Turn {turns}: {currentPlayer} turn",
                value=f"Enter a value from 1-{width}. You have 30 seconds to make a choice",
                inline=True,
            )
            await boardMessage.edit(embed=em)
            gotValidInput = False
            badInput = 0
            while not gotValidInput:
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda message: message.author.name == currentPlayer,
                        timeout=30,
                    )
                    await ctx.channel.delete_messages(await self.getMessages(ctx, 1))
                    slot = int(msg.content)
                    if slot < 1 or slot > width:
                        raise ValueError
                    # Place piece in slot
                    for y in range(height - 1, -1, -1):
                        if board[y][slot - 1] == s:
                            if currentPlayerId == 1:
                                board[y][slot - 1] = p1
                                break
                            else:
                                board[y][slot - 1] = p2
                                break
                        elif y == 0:  # if column is full
                            raise ValueError
                    # switch player
                    if currentPlayerId == 1:
                        currentPlayer = player1
                        otherPlayer = player2
                        currentPlayerId = 2
                    else:
                        currentPlayer = player1
                        otherPlayer = player2
                        currentPlayerId = 1
                    gotValidInput = True
                    turns += 1
                    break
                except asyncio.exceptions.TimeoutError:
                    winner = otherPlayer
                    winningComment = f"{currentPlayer} took too much time"
                    gameLoop = False
                    break
                except ValueError:
                    em = discord.Embed()
                    em.title = f"Connect 4"
                    em.description = f"{getDisplay()}"
                    em.color = 0x444444
                    em.add_field(
                        name=f"Turn {turns}: {currentPlayer}",
                        value=f"Enter a valid number from 1-{width}",
                        inline=False,
                    )
                    await boardMessage.edit(embed=em)
                    badInput += 1
                if badInput == 3:
                    winner = otherPlayer
                    winningComment = f"{currentPlayer} had too many bad inputs"
                    gameLoop = False
                    break
        if winner == None:
            em = discord.Embed()
            em.title = f"Connect 4 - Tie, No Winners"
            em.description = f"{getDisplay()}"
            em.color = 0x444444
            await boardMessage.edit(embed=em)
        elif winner == player1:
            em = discord.Embed()
            em.title = f"Connect 4 - {player1} wins!"
            em.description = f"{getDisplay()}"
            em.add_field(name="Reason:",
                         value=f"{winningComment}", inline=False)
            if player1 == player2:
                em.add_field(
                    name="Also:", value=f"They won against themself", inline=False
                )
            em.color = 0x444444
            await boardMessage.edit(embed=em)
        elif winner == player2:
            em = discord.Embed()
            em.title = f"Connect 4 - {player2} wins!"
            em.description = f"{getDisplay()}"
            em.add_field(name="Reason:",
                         value=f"{winningComment}", inline=False)
            if player1 == player2:
                em.add_field(
                    name="Also:", value=f"They won against themself", inline=False
                )
            em.color = 0x444444
            await boardMessage.edit(embed=em)


    @commands.command(name="21dares", aliases=["truth_or_dare"])
    async def tod(self, ctx, user: discord.Member = None, channel=discord.TextChannel):
        """21 truth or dare party game"""
        the_author = ctx.author
        channel = ctx.channel
        if user is None:
            embed = discord.Embed(
                title="Truth or Dare game",
                color=discord.Colour.orange(),
                description=f"{the_author.mention} is inviting anyone to play truth or dare! \n\nType `accept` now to accept the challenge and begin a game with them.",
            )
        elif user != the_author and not user.bot:
            embed = discord.Embed(
                title=" truth or dare",
                color=discord.Colour.orange(),
                description=f"{the_author.mention} is inviting anyone to play truth or dare! \n\nType `accept` now to accept the challenge and begin a game with them.",
            )
        else:
            embed = discord.Embed(
                title="You can't invite yourself or a discord bot to a game!"
            )

        msg = await channel.send(embed=embed)

        playerlist = []
        check_list = []
        count_list = []
        current_count = 0

        def checkConsecutive(l):
            return sorted(l) == list(range(min(l), max(l) + 1))

        def check(message):
            if message.channel == channel:
                return True

        while True:
            msg = await self.bot.wait_for("message", check=check)

            if msg.content == "accept":
                await ctx.send(
                    f"{msg.author.mention} accepted! type `start` before 60 seconds to start"
                )
                playerlist.append(msg.author)

            elif msg.content == "start" and len(playerlist) >= 2:
                await ctx.send(f"Game started!Start by typing `1 2 ..`")

                for player in itertools.cycle(playerlist):
                    embedlost = discord.Embed(
                        title=f"{player} lost! choose `Truth or Dare?!`"
                    )

                    def check1(message):
                        if message.author == player and message.channel == channel:

                            return True

                    await ctx.send(f"{player.mention}'s turn! :timer~1:")
                    n = await self.bot.wait_for("message", timeout=60.0, check=check1)
                    if n.content == "cancel" or n.content == "stop":
                        break

                    if n.author == player and n.author != self.bot.user:
                        listn = n.content.split(" ")
                        for element in listn:
                            element = int(element)
                            check_list.append(element)

                        if current_count >= 21 or 21 in check_list:
                            await ctx.send(embed=embedlost)
                            check_list.clear()
                            current_count = 0
                            break
                        elif check_list[0] == current_count + 1:

                            if checkConsecutive(check_list) == True:
                                for element in check_list:
                                    count_list.append(element)
                                current_count = count_list[-1]
                                check_list.clear()
                                await n.add_reaction("✅")
                            else:
                                await ctx.send(
                                    "Numbers not consecutive! YOU SPOLIED THE GAME! YOU LOSE!"
                                )
                                await ctx.send(embed=embedlost)
                                check_list.clear()
                                current_count = 0
                                break
                        else:
                            await ctx.send(
                                f"Dude you have to start from {current_count+1}! YOU SPOLIED THE GAME! YOU LOSE!"
                            )
                            await ctx.send(embed=embedlost)
                            check_list.clear()
                            current_count = 0
                            break

            elif msg.content == "start" and len(playerlist) < 2:
                await ctx.send("Can't start, less than 2 players")
            elif msg.content == "cancel":
                await ctx.send("Game Cancelled")
                break

    @commands.command()
    async def tic(self, ctx: commands.Context):
        """Starts a tic-tac-toe game with yourself."""
        await ctx.send("Tic Tac Toe: X goes first", view=TicTacToe())

    async def getMessages(self, ctx: commands.Context, number: int = 1):
        if number == 0:
            return []
        toDelete = []
        async for x in ctx.channel.history(limit=number):
            toDelete.append(x)
        return toDelete


    @commands.command(name="2048")
    async def twenty(self, ctx):
        """Play 2048 game"""
        await twenty.play(ctx, self.bot)

    @commands.command(name="hangman", aliases=["hang"])
    async def hangman(self, ctx):
        """Play Hangman"""
        await hangman.play(self.bot, ctx)

    @commands.command(name="rps", aliases=["rockpaperscissors"])
    async def rps(self, ctx):
        """Play Rock, Paper, Scissors game"""

        def check_win(p, b):
            if p == "🌑":
                return False if b == "📄" else True
            if p == "📄":
                return False if b == "✂" else True
            # p=='✂'
            return False if b == "🌑" else True

        async with ctx.typing():
            reactions = ["🌑", "📄", "✂"]
            game_message = await ctx.send(
                "**Rock Paper Scissors**\nChoose your shape:", delete_after=15.0
            )
            for reaction in reactions:
                await game_message.add_reaction(reaction)
            bot_emoji = random.choice(reactions)

        def check(reaction, user):
            return (
                user != self.bot.user
                and user == ctx.author
                and (str(reaction.emoji) == "🌑" or "📄" or "✂")
            )

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", timeout=10.0, check=check
            )
        except asyncio.TimeoutError:
            await ctx.send("Time's Up! :stopwatch:")
        else:
            await ctx.send(
                f"**:man_in_tuxedo_tone1:\t{reaction.emoji}\n:robot:\t{bot_emoji}**"
            )
            # if conds
            if str(reaction.emoji) == bot_emoji:
                await ctx.send("**It's a Tie :ribbon:**")
            elif check_win(str(reaction.emoji), bot_emoji):
                await ctx.send("**You win :sparkles:**")
            else:
                await ctx.send("**I win :robot:**")


def setup(bot):
    bot.add_cog(Games(bot))
