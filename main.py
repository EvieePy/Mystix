"""Copyright 2024 MystyPy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import logging

import discord

import core


LOGGER: logging.Logger = logging.getLogger("main")


def main() -> None:
    discord.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with core.Bot() as bot:
            await bot.start(core.CONFIG["DISCORD"]["TOKEN"])

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")


if __name__ == "__main__":
    main()
