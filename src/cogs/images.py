import io, os, discord, random, alexflipnote, aiohttp, contextlib
from discord.ext import commands
from PIL import Image, ImageDraw
from io import BytesIO
import requests
from utilities.helpers.utils import Votelink, voteembed
from PIL import ImageOps

import pyimgur

im = pyimgur.Imgur(os.getenv('IMGUR_API_KEY'))
afp = alexflipnote.Client(os.getenv("AFP_KEY"))

class Images(commands.Cog, name="Image", description="Image Commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.topggpy = bot.topggpy
        self.session = bot.httpsession

    def check_voted(self, userid):
        return self.bot.topggpy.get_user_vote(userid)

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

    @commands.command()
    async def wanted(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user

        wanted = Image.open("utilities/photos/wanted.jpg")
        asset = user.avatar.with_format("jpg")
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((252, 252))
        wanted.paste(pfp, (106, 247))
        wanted.save("profile.jpg")
        try:
            await ctx.send(file=discord.File("profile.jpg"))
            os.remove("profile.jpg")
        except:
            await ctx.send("Error!")

    @commands.command()
    async def kill(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user
        amogusimage = Image.open(f"utilities/photos/kill2.jfif")
        asset1 = user.avatar.with_format("jpg")
        asset2 = ctx.author.avatar.with_format("jpg")
        data1 = BytesIO(await asset1.read())
        data2 = BytesIO(await asset2.read())
        pfp = Image.open(data1)
        author = Image.open(data2)

        pfp = pfp.resize((55, 55))
        author = author.resize((55, 55))
        amogusimage.paste(author, (54, 58))
        amogusimage.paste(pfp, (170, 40))
        amogusimage.save("kill.jpg")
        try:
            await ctx.send(file=discord.File("kill.jpg"))
            os.remove("kill.jpg")
        except:
            await ctx.send("Error!")

    @commands.command()
    async def disfine(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user

        wanted = Image.open("utilities/photos/finelol.jpeg")
        asset = user.avatar.with_format("jpg")
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((350, 350))
        wanted.paste(pfp, (730, 335))
        wanted.save("finelol.jpg")
        try:
            await ctx.send(file=discord.File("finelol.jpg"))
            os.remove("finelol.jpg")
        except:
            await ctx.send("Error!")

    @commands.command()
    async def affect(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user

        wanted = Image.open("utilities/photos/affect.png")
        asset = user.avatar.with_format("png")
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((206, 162))
        wanted.paste(pfp, (176, 383))
        wanted.save("affectlol.jpg")
        await ctx.send(file=discord.File("affectlol.jpg"))
        os.remove("affectlol.jpg")

    @commands.command()
    async def dog(self, ctx):
       
        request = await self.session.get(
            "https://some-random-api.ml/img/dog"
        )  # Make a request
        dogjson = await request.json()  # Convert it to a JSON dictionary
        embed = discord.Embed(
            title="Doggo!", color=discord.Color.purple()
        )  # Create embed
        embed.set_image(
            url=dogjson["link"]
        )  # Set the embed image to the value of the 'link' key
        await ctx.send(embed=embed)  # Send the embed

    @commands.command()
    async def cat(self, ctx):
        
        request = await self.session.get(
            "https://some-random-api.ml/img/cat"
        )  # Make a request
        dogjson = await request.json()  # Convert it to a JSON dictionary
        embed = discord.Embed(
            title="CAT!", color=discord.Color.purple()
        )  # Create embed
        embed.set_image(
            url=dogjson["link"]
        )  # Set the embed image to the value of the 'link' key
        await ctx.send(embed=embed)  # Send the embed

    @commands.command(name="textart", aliases=["au"])
    async def font_generator(self, ctx, *, text: str = ""):
        """Generate cool font"""
        if not text:
            return await ctx.send("Please enter text :pager:")

        url = f"https://gdcolon.com/tools/gdfont/img/{text}?font=3&color=00ffff"
    
        async with self.session.get(url) as r:
            if r.status != 200:
                return await ctx.send("Failed to generate textart :x:")
            data = io.BytesIO(await r.read())
            await ctx.send(file=discord.File(data, "textart.png"))

    @commands.command()
    async def catgirl(self, ctx):
        
        request = await self.session.get(
            "http://api.nekos.fun:8080/api/neko"
        )  # Make a request
        dogjson = await request.json()  # Convert it to a JSON dictionary
        embed = discord.Embed(
            title="Catgirl", color=discord.Color.purple()
        )  # Create embed
        embed.set_image(
            url=dogjson["image"]
        )  # Set the embed image to the value of the 'link' key
        embed.set_footer(
            text="Image taken from Nekos.Fun api.\nDon't worry! There are no children or nsfw. Its just anime catgirls uwu"
        )
        await ctx.send(embed=embed)  # Send the embed
    
    @commands.command()
    async def achievement(self, ctx, *, text: str = ""):
        """Achievement unlocked"""
        if text == "":
            return await ctx.send("You need to specify the achievement")
        image = await afp.achievement(text=text)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "achievement.png"))

    @commands.command(aliases=["aij"])
    async def amiajoke(self, ctx, image=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.amiajoke(image)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "amiajoke.png"))

    @commands.command()
    async def drake(self, ctx, *, text):
        text = text.split(",")
        if len(text) != 2:
            return await ctx.send(
                "Please specify `,` separated two sentences :page_facing_up:"
            )
        image = await afp.drake(text[0], text[1])
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "drake.png"))

    @commands.command()
    async def bad(self, ctx, image=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.bad(image)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "bad.png"))

    @commands.command()
    async def birb(self, ctx):
        image = await afp.birb()
        # image_bytes = await image.read()
        await ctx.send(image)

    @commands.command()
    async def coffee(self, ctx):
        image = await afp.coffee()
        # image_bytes = await image.read()
        await ctx.send(image)

    @commands.command()
    async def calling(self, ctx, *, text: str = ""):
        """Call meme"""
        if text == "":
            return await ctx.send("You need to specify the text")
        image = await afp.calling(text=text)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "call.png"))

    @commands.command()
    async def captcha(self, ctx, *, text: str = ""):
        """Make a custom fake captcha!!"""
        if text == "":
            return await ctx.send("You need to specify the text")
        image = await afp.captcha(text=text)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "captcha.png"))

    @commands.command()
    async def colourify(self, ctx, image=None, colour=None, background=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.colourify(image, colour, background)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "colourify.png"))

    @commands.command()
    async def didumean(self, ctx, *, text):
        text = text.split(",")
        if len(text) != 2:
            return await ctx.send(
                "Please specify `,` separated two sentences :page_facing_up:"
            )
        if len(text[0]) > 39 or len(text[1]) > 39:
            return await ctx.send("Your text is too big. limit is 40 characters")
        image = await afp.did_you_mean(text[0], text[1])
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "didumean.png"))

    @commands.command()
    async def factimage(self, ctx, *, text: str = ""):
        """Make a custom fake fact image!!"""
        if text == "":
            return await ctx.send("You need to specify the text")
        image = await afp.facts(text=text)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "facts.png"))

    @commands.command(
        name="filter",
        aliases=[
            "blur",
            "b&w",
            "deepfry",
            "sepia",
            "pixelate",
            "magik",
            "jpegify",
            "wide",
            "snow",
            "gay",
            "communist",
        ],
    )
    async def filter(self, ctx, arg="", image_link=""):
        """Deepfry avatar"""

        if not await self.check_voted(ctx.author.id) == True:
            await ctx.send(embed=voteembed, view=Votelink())

        filters = [
            "b&w",
            "blur",
            "charcoal",
            "communist",
            "deepfry",
            "edge",
            "emboss",
            "gay",
            "glitch",
            "implode",
            "jpegify",
            "magik",
            "pixelate",
            "primitive",
            "sepia",
            "sketch",
            "snow",
            "spread",
            "swirl",
            "wave",
            "wide",
        ]
        if arg == "--list":
            return await ctx.send(
                embed=discord.Embed(title="Filters", description="\n".join(filters))
            )
        if arg not in filters:
            return await ctx.send(
                "Invalid filter name\nUse `.filter --list` for all options"
            )

        if not image_link:
            user = ctx.message.author
            image_link = user.avatar.url
        try:
            user = ctx.message.mentions[0]
            image_link = user.avatar.url
        except IndexError:
            pass

        image = await afp.filter(arg, image_link)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "filtered.png"))

    @commands.command()
    async def floor(self, ctx, image=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.floor(image)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "floor.png"))

    @commands.command()
    async def fml(self, ctx):
        image = await afp.fml()
        # image_bytes = await image.read()
        await ctx.send(image)

    @commands.command()
    async def salty(self, ctx, image=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.salty(image)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "salty.png"))

    @commands.command()
    async def shame(self, ctx, image=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.shame(image)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "salty.png"))

    @commands.command()
    async def scroll(self, ctx, *, text: str = ""):
        if text == "":
            return await ctx.send("You need to specify the text")
        image = await afp.scroll(text=text)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "scroll.png"))

    @commands.command()
    async def ship(
        self, ctx, member1: discord.Member = None, member2: discord.Member = None
    ):
        if member1 == None:
            member1 = ctx.author
        if member2 == None:
            return await ctx.send("You need to specify a user to be shipped with!")

        ppurl1 = member1.avatar.url
        ppurl2 = member2.avatar.url

        random.seed(member1.id + member2.id)
        r = random.randint(1, 100)
        shipper = r / 1.17

        image = await afp.ship(ppurl1, ppurl2)
        image_bytes = await image.read()

        draw = ImageDraw.Draw(image_bytes)
        draw.text((28, 36), shipper, fill=(255, 0, 0))

        await ctx.send(file=discord.File(image_bytes, "ship.png"))

    @commands.command()
    async def what(self, ctx, image=None):
        if image == None:
            image = ctx.author.avatar.url
        image = await afp.what(image)
        image_bytes = await image.read()
        await ctx.send(file=discord.File(image_bytes, "what.png"))

    @commands.command()
    async def imgur(self, ctx, image_url=None):
        if image_url == None:
            return await ctx.send(
                "Usage: .imgur <discord image link ending with `.png` or `.jpg`>"
            )

        myfile = requests.get(image_url)
        open("utilities/photos/imgur.png", "wb").write(myfile.content)

        try:
            uploaded_image = im.upload_image(
                "utilities/photos/imgur.png", title=f"Uploaded by SpaceBot"
            )
        except:
            await ctx.send(
                "Error: either the link is invalid(it should end with .png or any other picture format, or i couldnt process the image"
            )
        await ctx.send(
            embed=discord.Embed(
                title="Upload successful",
                description=f"Successfully uploaded image to imgur `LINK`- {uploaded_image.link}",
            )
        )

    async def invert_image(
        self,
        ctx: commands.Context,
        url,
        image_type: str,
    ):
        # Some of this image/url handling came from Red-DiscordBot, thanks
        await ctx.trigger_typing()
        if len(ctx.message.attachments) > 0:
            data = await ctx.message.attachments[0].read()
        else:
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as r:
                        data = await r.read()
                except aiohttp.InvalidURL:
                    return await ctx.send("That URL is invalid.")
                except aiohttp.ClientError:
                    return await ctx.send("Something went wrong while trying to get the image.")

        data = io.BytesIO(data)
        try:
            image = Image.open(data)
            image = ImageOps.invert(image.convert("RGB"))
        except Exception:
            return await ctx.send(
                "Failed to invert. Make sure that you have provided an image and in the correct format."
            )

        buff = io.BytesIO()
        image.save(buff, "png")
        buff.seek(0)
        embed = discord.Embed(
            title=f"Inverted {image_type.capitalize()}",
            color=discord.Colour.random(),
        )
        try:
            embed.set_image(url="attachment://image.png")
            await ctx.send(file=discord.File(buff, filename="image.png"), embed=embed)
        except discord.HTTPException:
            await ctx.send("The image quality was too high, sorry!")
            return

    @commands.group()
    async def invert(self, ctx: commands.Context):
        """Invert images and avatars."""

    @invert.command()
    async def image(self, ctx, url: str = None):
        """Invert an image.
        You can either upload an image or paste a URL.
        """
        if not any([url, ctx.message.attachments]):
            return await ctx.send_help()
        msg = await ctx.send("Inverting image...")
        await self.invert_image(
            ctx=ctx,
            url=url,
            image_type="image",
        )
        with contextlib.suppress(discord.NotFound):
            await msg.delete()

    @invert.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """Invert a user's avatar.
        If no user is provided, it defaults to yourself.
        """
        msg = await ctx.send("Inverting avatar...")
        if not member:
            member = ctx.author
        avvy = str(member.avatar.url)
        await self.invert_image(
            ctx=ctx,
            url=avvy,
            image_type="avatar",
        )
        with contextlib.suppress(discord.NotFound):
            await msg.delete()

def setup(bot):
  bot.add_cog(Images(bot))