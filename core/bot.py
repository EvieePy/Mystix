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

import logging

import discord
from discord.ext import commands


LOGGER: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix=["m! ", "m!"], help_command=None)

    async def setup_hook(self) -> None:
        await self.load_extension("extensions", package="extensions")

    async def on_ready(self) -> None:
        LOGGER.info("Logged in | %s", self.user)
