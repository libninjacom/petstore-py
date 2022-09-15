import os
import aiohttp
import asyncio
import json
import logging
from .logger import logger
from .authenticator import PetstoreAuthenticator
from typing import Optional, List, Any, Dict
from . import model


def filter_none(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


class AsyncPetstoreClient:
    def __init__(self, base_url: str, authenticator: PetstoreAuthenticator):
        self.authenticator = authenticator
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "petstore/python/0.1.1",
                "Content-Type": "application/json",
            }
        )

    async def send(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        data: Dict[str, Any],
        decode: bool,
    ) -> Dict[str, Any]:
        headers = filter_none(headers)
        params = filter_none(params)
        data = filter_none(data)
        do_debug = logger.getEffectiveLevel() == logging.DEBUG
        if do_debug:
            logger.debug(
                json.dumps(
                    dict(
                        method=method,
                        url=url,
                        headers=dict(**headers, **self.session.headers),
                        params=params,
                        json=data,
                    )
                )
            )
        async with self.session.request(
            method, url, headers=headers, params=params, json=data
        ) as res:
            if do_debug:
                data = dict(
                    status_code=res.status,
                    headers=dict(**res.headers),
                )
                try:
                    data["json"] = await res.json()
                except json.JSONDecodeError:
                    data["body"] = await res.text()
                logger.debug(json.dumps(data))
            if not res.ok:
                content = await res.text()
                res.release()
                raise aiohttp.ClientResponseError(
                    res.request_info,
                    res.history,
                    status=res.status,
                    message=content,
                    headers=res.headers,
                )
            if decode:
                data = await res.json()
                return data
            else:
                return {}

    async def list_pets(self, limit: Optional[int] = None) -> model.Pets:
        """List all pets"""
        headers: Dict[str, str | None] = {}
        params: Dict[str, str | None] = {
            "limit": limit,
        }
        data: Dict[str, Any] = {}

        data = await self.send(
            "GET", self.base_url + "/pets", headers, params, data, True
        )
        return model.Pets.parse_obj(data)

    async def create_pets(self) -> None:
        """Create a pet"""
        headers: Dict[str, str | None] = {}
        params: Dict[str, str | None] = {}
        data: Dict[str, Any] = {}

        data = await self.send(
            "POST", self.base_url + "/pets", headers, params, data, False
        )
        return None

    async def show_pet_by_id(self, pet_id: int) -> model.Pet:
        """Info for a specific pet"""
        headers: Dict[str, str | None] = {}
        params: Dict[str, str | None] = {}
        data: Dict[str, Any] = {}

        data = await self.send(
            "GET", self.base_url + f"/pets/{pet_id}", headers, params, data, True
        )
        return model.Pet.parse_obj(data)

    def __del__(self) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.session.close())
            else:
                loop.run_until_complete(self.session.close())
        except Exception:
            pass

    @classmethod
    def from_env(cls) -> "AsyncPetstoreClient":
        url = os.environ["PETSTORE_BASE_URL"]
        return cls(base_url=url, authenticator=PetstoreAuthenticator.from_env())
