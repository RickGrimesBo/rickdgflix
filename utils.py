from aiohttp import ClientSession
from exceptions import GdFlixError

class GdFlix:
    def __init__(self, api_key: str, base_uri: str) -> None:
        self._api_key = api_key
        self._base_uri = base_uri

    async def share_file(self, file_id: str):
        res = await self._http_get(f"{self._base_uri}/share?key={self._api_key}&id={file_id}")
        if res.get("error"):
            raise GdFlixError(res.get("message"))
        return res

    async def _http_get(self, url: str) -> dict:
        async with ClientSession() as session:
            async with session.get(url) as response:
                return await response.json(content_type=None)