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
from typing import Any, cast

import discord
import tweepy.asynchronous  # type: ignore
from discord.ext import commands, tasks

import core


LOGGER: logging.Logger = logging.getLogger(__name__)


class Twitter(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot = bot
        self.tclient = tweepy.asynchronous.AsyncClient(
            bearer_token=core.CONFIG["TWITTER"]["TOKEN"],
            return_type=dict,  # type: ignore
            wait_on_rate_limit=True,
        )

        # self.TWITTER_FEED: int = 1313962135185002547
        self.TWITTER_FEED: int = 1313934259274387536
        self.last_id: int = 0

    def build_embed(self, data: ..., /) -> discord.Embed: ...

    async def cog_load(self) -> None:
        self.last_id: int = core.CONFIG["TWITTER"]["last_id"]
        self.fetch_dofus_tweets.start()

    @tasks.loop(minutes=15)
    async def fetch_dofus_tweets(self) -> None:
        channel: discord.TextChannel | None = cast(discord.TextChannel | None, self.bot.get_channel(self.TWITTER_FEED))

        if not channel:
            LOGGER.warning("Could not find or access the Dofus Twittter Feed Channel...")
            return

        query = "from:DOFUS_EN -is:reply"
        data: dict[str, Any] = await self.tclient.search_recent_tweets(  # type: ignore
            query, max_results=10, since_id=self.last_id, user_auth=False
        )

        await channel.send(str(data))

    @fetch_dofus_tweets.before_loop
    async def dofus_tweets_before(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Twitter(bot))
