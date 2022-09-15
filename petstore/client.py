import os
import json
import logging
import requests
from typing import Optional, List, Any, Dict
from .authenticator import PetstoreAuthenticator
from .logger import logger
from . import model


def raise_for_status(res: requests.Response) -> None:
    if res.status_code >= 400:
        try:
            content = res.json()
        except requests.JSONDecodeError:
            content = res.content
        raise requests.HTTPError(content, response=res)


def log_prepped_request(
    req: requests.Request, prepped: requests.PreparedRequest
) -> None:
    data = dict(
        method=prepped.method,
        url=prepped.url,
        headers=dict(prepped.headers),
    )
    if req.json is not None:
        data["json"] = req.json
    elif type(prepped.body) is bytes:
        data["body"] = prepped.body.decode("utf-8")
    elif type(prepped.body) is str:
        data["body"] = prepped.body
    logger.debug(json.dumps(data))


def log_response(res: requests.Response) -> None:
    data = dict(
        status_code=res.status_code,
        headers=dict(res.headers),
    )
    try:
        data["json"] = res.json()
    except requests.JSONDecodeError:
        data["body"] = res.text
    logger.debug(json.dumps(data))


class PetstoreClient:
    def __init__(self, base_url: str, authenticator: PetstoreAuthenticator):
        self.authenticator = authenticator
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["User-Agent"] = "petstore/python/0.1.1"

    def send(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        data: Dict[str, Any],
    ) -> requests.Response:
        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
        )
        prepped = req.prepare()
        do_debug = logger.getEffectiveLevel() == logging.DEBUG
        if do_debug:
            log_prepped_request(req, prepped)
        res = self.session.send(prepped)
        if do_debug:
            log_response(res)
        raise_for_status(res)
        return res

    def list_pets(self, limit: Optional[int] = None) -> model.Pets:
        """List all pets"""
        headers: Dict[str, str | None] = {}
        params: Dict[str, str | None] = {
            "limit": limit,
        }
        data: Dict[str, Any] = {}

        res = self.send("GET", self.base_url + "/pets", headers, params, data)
        data = res.json()
        return model.Pets.parse_obj(data)

    def create_pets(self) -> None:
        """Create a pet"""
        headers: Dict[str, str | None] = {}
        params: Dict[str, str | None] = {}
        data: Dict[str, Any] = {}

        res = self.send("POST", self.base_url + "/pets", headers, params, data)
        return None

    def show_pet_by_id(self, pet_id: int) -> model.Pet:
        """Info for a specific pet"""
        headers: Dict[str, str | None] = {}
        params: Dict[str, str | None] = {}
        data: Dict[str, Any] = {}

        res = self.send("GET", self.base_url + f"/pets/{pet_id}", headers, params, data)
        data = res.json()
        return model.Pet.parse_obj(data)

    @classmethod
    def from_env(cls) -> "PetstoreClient":
        url = os.environ["PETSTORE_BASE_URL"]
        return cls(base_url=url, authenticator=PetstoreAuthenticator.from_env())
