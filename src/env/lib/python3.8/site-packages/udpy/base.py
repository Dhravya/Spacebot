import sys
import json
import requests
import typing
import aiohttp

from urllib.parse import quote as urlquote

UD_DEFID_URL = 'https://api.urbandictionary.com/v0/define?defid='
UD_DEFINE_URL = 'https://api.urbandictionary.com/v0/define?term='
UD_RANDOM_URL = 'https://api.urbandictionary.com/v0/random'

class UrbanDefinition(object):
    def __init__(self, word: str, definition: str, example: str, upvotes: int, downvotes: int):
        self.word = word
        self.definition = definition
        self.example = example
        self.upvotes = upvotes
        self.downvotes = downvotes

    def __str__(self):
        return '%s: %s%s (%d, %d)' % (
                self.word,
                self.definition[:50],
                '...' if len(self.definition) > 50 else '',
                self.upvotes,
                self.downvotes
            )

class UrbanClient:
    def __init__(self, session: typing.Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def _request(self, url: str) -> dict:
        result = self.session.get(url)
        return result.json()
    
    def get_definition(self, term: str) -> UrbanDefinition:
        json = self._request(UD_DEFINE_URL + urlquote(term))
        return _parse(json)

    def get_definition_by_id(self, id: int) -> UrbanDefinition:
        json = self._request(UD_DEFID_URL + urlquote(str(defid)))
        return _parse(json)

    def get_random_definition(self) -> UrbanDefinition:
        json = self._request(UD_RANDOM_URL)
        return _parse(json, check_result=False)


def _parse(json: dict, check_result: bool = True) -> UrbanDefinition:
    result = []
    if json is None or any(e in json for e in ('error', 'errors')):
        raise ValueException('UD: Invalid input for Urban Dictionary API')
    if check_result and ('list' not in json or len(json['list']) == 0):
        return result
    for definition in json['list']:
        d = UrbanDefinition(
                definition['word'], 
                definition['definition'],
                definition['example'],
                int(definition['thumbs_up']),
                int(definition['thumbs_down'])
            )
        result.append(d)
    return result


class AsyncUrbanClient:
    def __init__(self, session: typing.Optional[aiohttp.ClientSession] = None):
        self.session = session or aiohttp.ClientSession()

    async def _request(self, url: str) -> dict:
        async with self.session.get(url) as resp:
            return await resp.json()
    
    async def get_definition(self, term: str) -> UrbanDefinition:
        json = await self._request(UD_DEFINE_URL + urlquote(term))
        return _parse(json)

    async def get_definition_by_id(self, id: int) -> UrbanDefinition:
        json = await self._request(UD_DEFID_URL + urlquote(str(defid)))
        return _parse(json)

    async def get_random_definition(self) -> UrbanDefinition:
        json = await self._request(UD_RANDOM_URL)
        return _parse(json, check_result=False)
