from enum import Enum
from io import BytesIO
from typing import List, Union

from aiohttp import ClientResponse


class Image:
    __slots__ = ("url", "_response")

    def __init__(self, response: ClientResponse) -> None:
        self.url: str = str(response.url)
        self._response: ClientResponse = response

    def __str__(self) -> str:
        return self.url

    async def read(self, bytesio = True) -> Union[bytes, BytesIO]:
        _bytes = await self._response.read()
        if bytesio is False:
            return _bytes

        return BytesIO(_bytes)


class Colour:
    __slots__ = (
        "blackorwhite_text",
        "brightness",
        "hex",
        "image",
        "image_gradient",
        "int",
        "name",
        "rgb",
        "rgb_values",
        "shade",
        "tint",
        )

    def __init__(self, data) -> None:
        self.blackorwhite_text: str = data.get("blackorwhite_text")
        self.brightness: int = data.get("brightness")
        self.hex: str = data.get("hex")
        self.image: str = data.get("image")
        self.image_gradient: str = data.get("image_gradient")
        self.int: int = data.get("int")
        self.name: str = data.get("name")
        self.rgb: str = data.get("rgb")
        self.rgb_values: Colour.ColourRGB = Colour.ColourRGB(data.get("rgb_values"))
        self.shade: List[str] = data.get("shade")
        self.tint: List[str] = data.get("tint")

    class ColourRGB:
        __slots__ = ("all", "r", "g", "b")

        def __init__(self, data) -> None:
            self.all: dict = data
            self.r: int = data.get("r")
            self.g: int = data.get("g")
            self.b: int = data.get("b")


class MinecraftIcons(Enum):
    GRASS_BLOCK = 1
    DIAMOND = 2
    DIAMOND_SWORD = 3
    CREEPER = 4
    PIG = 5
    TNT = 6
    COOKIE = 7
    HEART = 8
    BED = 9
    CAKE = 10
    SIGN = 11
    RAIL = 12
    CRAFTING_BENCH = 13
    REDSTONE = 14
    FIRE = 15
    COBWEB = 16
    CHEST = 17
    FURNACE = 18
    BOOK = 19
    STONE_BLOCK = 20
    WOODEN_PLANK_BLOCK = 21
    IRON_INGOT = 22
    GOLD_INGOT = 23
    WOODEN_DOOR = 24
    IRON_DOOR = 25
    DIAMOND_CHESTPLATE = 26
    FLINT_AND_STEEL = 27
    GLASS_BOTTLE = 28
    SPLASH_POTION = 29
    CREEPER_SPAWNEGG = 30
    COAL = 31
    IRON_SWORD = 32
    BOW = 33
    ARROW = 34
    IRON_CHESTPLATE = 35
    BUCKET = 36
    BUCKET_WITH_WATER = 37
    BUCKET_WITH_LAVA = 38
    BUCKET_WITH_MILK = 39
    DIAMOND_BOOTS = 40
    WOODEN_HOE = 41
    BREAD = 42
    WOODEN_SWORD = 43
    BONE = 44
    OAK_LOG = 45
    RANDOM = 46

    # ALIASES -------------------
    GRASSBLOCK = 1
    DIAMONDSWORD = 3
    CRAFTINGBENCH = 13
    STONEBLOCK = 20
    WOODENPLANKBLOCK = 21
    IRONINGOT = 22
    GOLDINGOT = 23
    WOODENDOOR = 24
    IRONDOOR = 25
    DIAMONDCHESTPLATE = 26
    FLINTANDSTEEL = 27
    GLASSBOTTLE = 28
    SPLASHPOTION = 29
    CREEPERSPAWNEGG = 38
    IRONSWORD = 32
    IRONCHESTPLATE = 35
    BUCKETWITHWATER = 37
    BUCKETWITHLAVA = 38
    BUCKETWITHMILK = 39
    DIAMONDBOOTS = 40
    WOODENHOE = 41
    WOORDENSWORD = 43
    OAKLOG = 45


class Filters(Enum):
    BLUR = 1
    INVERT = 2
    BLACK_AND_WHITE = 3  # b&w
    DEEPFRY = 4
    SEPIA = 5
    PIXELATE = 6
    MAGIK = 7
    JPEGIFY = 8
    WIDE = 9
    FLIP = 10
    MIRROR = 11
    SNOW = 12
    GAY = 13
    COMMUNIST = 14
    RANDOM = 15
