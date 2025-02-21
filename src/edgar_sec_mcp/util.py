import httpx


async def _make_request(method: str, url: str, **kwargs):
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url=url, **kwargs)
        response.raise_for_status()
        return response


async def async_http_get(url, **kwargs):
    return await _make_request("GET", url, **kwargs)


async def async_http_post(url, **kwargs):
    return await _make_request("POST", url, **kwargs)
