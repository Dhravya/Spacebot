import inspect
from asyncio import AbstractEventLoop
from random import choice, randint
from re import search
from typing import Any, List, Match, Optional, Tuple, Union
from urllib.parse import quote, urlencode

from .classes import Colour, Filters, Image, MinecraftIcons
from .errors import BadRequest, Forbidden, HTTPException, InternalServerError, MissingToken, NotFound
from .http import aiohttp, HTTPSession


def _GENERATE_COLOUR(numbers: Optional[int] = None) -> str:
    random_number = numbers or randint(0, 16777215)
    hex_number = str(hex(random_number))
    return hex_number[2:]


def _IS_VALID_HEX_VALUE(hex_input: Union[str, int]) -> Tuple[bool, str]:
    if isinstance(hex_input, int):
        hex_input = _GENERATE_COLOUR(int(hex_input))

    _INVALID_HEX_VALUE_ERROR = "Invalid HEX value. You're only allowed to enter HEX (0-9 & A-F, #..., 0x...)"
    match: Optional[Match[str]] = search(r"^#?(?:[0-9a-fA-F]{3}){1,2}$", str(hex_input))
    return (True, match.string.strip("#")) if match else (False, str(_INVALID_HEX_VALUE_ERROR))


def _get_from_enum(enum_class: Any, value: Union[str, int]) -> Any:
    try:
        if isinstance(value, str):
            val = enum_class[str(value.upper())]
        elif isinstance(value, int):
            val = enum_class(int(value))
        else:
            val = value

        return val
    except (KeyError, ValueError):
        return None


async def _get_error_message(response: aiohttp.ClientResponse) -> str:
    if response.content_type == "application/json":
        return str((await response.json()).get("description", None))
    return str(await response.text())


class Client:
    _BASE_URL: str = "https://api.alexflipnote.dev"
    _BASE_URL_COFFEE: str = "https://coffee.alexflipnote.dev"

    __slots__ = ("token", "_session", "loop")

    def __init__(
            self,
            token: str = None,
            *,
            session: aiohttp.ClientSession = None,
            loop: AbstractEventLoop = None
            ) -> None:
        self.token: str = token
        self._session: aiohttp.ClientSession = session or HTTPSession(loop = loop)

    async def _api_request(self, endpoint: str = None, params: dict = None):
        TOKEN_NOT_REQUIRED: List[str] = ["colour", "colour_image", "colour_image_gradient",
                                         "birb", "dogs", "sadcat", "cats", "coffee"]
        called_from_function: str = str(inspect.stack()[1].function).lower()
        if self.token is None and called_from_function not in TOKEN_NOT_REQUIRED:
            raise MissingToken(called_from_function)

        headers = {}
        if self.token and called_from_function not in TOKEN_NOT_REQUIRED:
            headers["Authorization"] = str(self.token).strip()

        url = f"{self._BASE_URL}/{endpoint}"
        if params:
            encoded_param = urlencode(params, quote_via = quote)
            url += f"?{encoded_param}"

        # random coffee api
        if called_from_function == "coffee":
            url = f"{self._BASE_URL_COFFEE}/random.json"

        response = await self._session.get(str(url), headers = headers)

        if response.status == 200:
            if response.content_type == "application/json":
                return await response.json()
            return response

        elif response.status == 400:
            raise BadRequest(await _get_error_message(response))
        elif response.status == 403:
            raise Forbidden(await _get_error_message(response))
        elif response.status == 404:
            raise NotFound(await _get_error_message(response))
        elif response.status == 500:
            raise InternalServerError(await _get_error_message(response))
        else:
            raise HTTPException(response, await _get_error_message(response))

    # Animals / JSON

    async def birb(self) -> str:
        json_response = await self._api_request("birb")
        return json_response.get('file')

    async def cats(self) -> str:
        json_response = await self._api_request("cats")
        return json_response.get('file')

    async def sadcat(self) -> str:
        json_response = await self._api_request("sadcat")
        return json_response.get('file')

    async def fml(self) -> str:
        json_response = await self._api_request("fml")
        return json_response.get("text")

    async def dogs(self) -> str:
        json_response = await self._api_request("dogs")
        return json_response.get('file')

    async def coffee(self) -> str:
        json_response = await self._api_request()
        return json_response.get('file')

    # Colour

    async def colour(self, colour: Union[str, int] = None) -> Colour:
        if not colour:
            colour: str = _GENERATE_COLOUR()
        else:
            check_colour = _IS_VALID_HEX_VALUE(colour)
            if check_colour[0] is False:
                raise BadRequest(check_colour[1])
            colour = check_colour[1]

        color = await self._api_request(f"colour/{colour}")
        return Colour(color)

    async def colour_image(self, colour: Union[str, int] = None) -> Image:
        if not colour:
            colour: str = _GENERATE_COLOUR()
        else:
            check_colour = _IS_VALID_HEX_VALUE(colour)
            if check_colour[0] is False:
                raise BadRequest(check_colour[1])
            colour = check_colour[1]

        response = await self._api_request(f"colour/image/{colour}")
        return Image(response)

    async def colour_image_gradient(self, colour: Union[str, int] = None) -> Image:
        if not colour:
            colour: str = _GENERATE_COLOUR()
        else:
            check_colour = _IS_VALID_HEX_VALUE(colour)
            if check_colour[0] is False:
                raise BadRequest(check_colour[1])
            colour = check_colour[1]

        response = await self._api_request(f"colour/image/gradient/{colour}")
        return Image(response)

    async def colourify(self, image: str, colour: Union[str, int] = None, background: Union[str, int] = None) -> Image:
        params = {"image": str(image)}
        if colour:
            check_colour = _IS_VALID_HEX_VALUE(colour)
            if check_colour[0] is False:
                raise BadRequest(check_colour[1])
            colour = check_colour[1]

            params["c"] = colour

        if background:
            check_colour = _IS_VALID_HEX_VALUE(background)
            if check_colour[0] is False:
                raise BadRequest(check_colour[1])
            background = check_colour[1]

            params["b"] = background

        response = await self._api_request("colourify", params)
        return Image(response)

    # Minecraft

    async def achievement(self, text: str, icon: Union[str, int, MinecraftIcons] = MinecraftIcons.RANDOM) -> Image:
        get_icon = _get_from_enum(MinecraftIcons, icon)
        if get_icon is MinecraftIcons.RANDOM or not get_icon:
            icon = choice(list(MinecraftIcons)).value
        else:
            icon = get_icon.value

        response = await self._api_request("achievement", {"text": str(text), "icon": int(icon)})
        return Image(response)

    async def challenge(self, text: str, icon: Union[str, int, MinecraftIcons] = MinecraftIcons.RANDOM) -> Image:
        get_icon = _get_from_enum(MinecraftIcons, icon)
        if get_icon is MinecraftIcons.RANDOM or not get_icon:
            icon = choice(list(MinecraftIcons)).value
        else:
            icon = get_icon.value

        response = await self._api_request("challenge", {"text": str(text), "icon": int(icon)})
        return Image(response)

    # Image

    async def amiajoke(self, image: str) -> Image:
        response = await self._api_request("amiajoke", {"image": str(image)})
        return Image(response)

    async def bad(self, image: str) -> Image:
        response = await self._api_request("bad", {"image": str(image)})
        return Image(response)

    async def calling(self, text: str) -> Image:
        response = await self._api_request("calling", {"text": str(text)})
        return Image(response)

    async def captcha(self, text: str) -> Image:
        response = await self._api_request("captcha", {"text": str(text)})
        return Image(response)

    async def did_you_mean(self, top: str, bottom: str) -> Image:
        response = await self._api_request("didyoumean", {"top": str(top), "bottom": str(bottom)})
        return Image(response)

    async def drake(self, top: str, bottom: str, *, ayano: bool = False) -> Image:
        params = {"top": str(top), "bottom": str(bottom)}
        if ayano:
            params["ayano"] = bool(ayano)
        response = await self._api_request("drake", params)
        return Image(response)

    async def facts(self, text: str) -> Image:
        response = await self._api_request("facts", {"text": str(text)})
        return Image(response)

    async def filter(self, name: Union[str, int, Filters], image: str) -> Image:
        if isinstance(name, str):
            if name == "b&w":  # any better way ?
                name = Filters.BLACK_AND_WHITE
        get_filter = _get_from_enum(Filters, name)
        if not get_filter:
            all_filters = [
                fil.name.lower().replace("black_and_white", "b&w")
                for fil in list(Filters)
                ]
            raise NotFound(f"Filter not found. Valid options: {', '.join(all_filters)}")
        if get_filter is Filters.RANDOM:
            name = choice(list(Filters)).name
        else:
            name = get_filter.name

        name = name.replace("BLACK_AND_WHITE", "b&w")

        response = await self._api_request(f"filter/{name.lower()}", {"image": str(image)})
        return Image(response)

    async def floor(self, text: str, image: str = None) -> Image:
        params = {"text": str(text)}
        if image:
            params["image"] = str(image)

        response = await self._api_request("floor", params)
        return Image(response)

    async def joke_overhead(self, image: str) -> Image:
        response = await self._api_request("jokeoverhead", {"image": str(image)})
        return Image(response)

    async def pornhub(self, text: str, text2: str) -> Image:
        response = await self._api_request("pornhub", {"text": str(text), "text2": str(text2)})
        return Image(response)

    async def salty(self, image: str) -> Image:
        response = await self._api_request("salty", {"image": str(image)})
        return Image(response)

    async def scroll(self, text: str) -> Image:
        response = await self._api_request(f"scroll", {"text": str(text)})
        return Image(response)

    async def ship(self, user: str, user2: str) -> Image:
        response = await self._api_request("ship", {"user": str(user), "user2": str(user2)})
        return Image(response)

    async def supreme(self, text: str, dark: bool = False, light: bool = False) -> Image:
        params = {"text": str(text)}
        if dark:
            params["dark"] = "true"
        if light:
            params["light"] = "true"

        response = await self._api_request("supreme", params)
        return Image(response)

    async def trash(self, face: str, trash: str) -> Image:
        response = await self._api_request("trash", {"face": str(face), "trash": str(trash)})
        return Image(response)

    async def what(self, image: str) -> Image:
        response = await self._api_request("what", {"image": str(image)})
        return Image(response)

    async def shame(self, image: str) -> Image:
        response = await self._api_request("shame", {"image": str(image)})
        return Image(response)

    # Other

    async def support_server(self, creator: bool = False) -> Union[str, Tuple]:
        api = await self._session.get(self._BASE_URL)
        discord_server = (await api.json()).get("support_server")
        if creator:
            return discord_server, "https://discord.gg/yCzcfju"

        return discord_server

    # Aliases

    didyoumean = did_you_mean
    discord_server = support_server
    color = colour
    colorify = colourify
    color_image = colour_image
    color_image_gradient = colour_image_gradient
    jokeoverhead = joke_overhead

    # Session

    async def close(self) -> None:
        await self._session.close()
