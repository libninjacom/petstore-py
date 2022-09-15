import os
from petstore import AsyncPetstoreClient
from petstore import PetstoreClient


def main():
    client = PetstoreClient.from_env()
    response = client.list_pets()
    print(f"{response!r}")


async def async_main():
    client = AsyncPetstoreClient.from_env()
    response = await client.list_pets()
    print(f"{response!r}")


if __name__ == "__main__":
    if os.environ.get("ASYNC"):
        import asyncio

        asyncio.run(async_main())
    else:
        main()
