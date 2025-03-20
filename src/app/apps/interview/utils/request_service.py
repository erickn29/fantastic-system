from typing import Protocol

import aiohttp


class RequestServiceProtocol(Protocol):
    def __init__(self, url: str):
        """Инициализирует сервис запросов"""
        pass

    async def send_request_llm(self, data: dict) -> dict | None:
        """Отправляет запрос к сервису и получает ответ"""
        pass


class RequestService:
    def __init__(self, url: str):
        self._url = url

    async def send_request_llm(self, data: dict) -> dict | None:
        """Отправляет запрос к сервису и получает ответ"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self._url, json=data, headers={"Content-Type": "application/json"}
            ) as response,
        ):
            try:
                return await response.json()
            except aiohttp.ClientError:
                return None
