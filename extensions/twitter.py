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

import datetime
import json
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

        self.TWITTER_FEED: int = 1313962135185002547
        self.last_id: int = 0

    def build_embed(
        self,
        data: dict[str, Any],
        /,
        *,
        thumb: str,
        username: str,
        image: str | None = None,
    ) -> discord.Embed:
        URL: str = f"https://x.com/{username}"

        embed = discord.Embed(description=f'### [@{username}]({URL})\n\n{data["text"]}', color=0xE4A047)
        embed.set_thumbnail(url=thumb)
        embed.set_author(name="View on x.com", url=f"{URL}/status/{data['id']}")

        if image:
            embed.set_image(url=image)

        embed.timestamp = datetime.datetime.fromisoformat(data["created_at"])
        return embed

    async def cog_load(self) -> None:
        self.last_id: int = core.CONFIG["TWITTER"]["last_id"]
        self.fetch_dofus_tweets.start()

    async def cog_unload(self) -> None:
        self.fetch_dofus_tweets.cancel()

    @tasks.loop(minutes=15)
    async def fetch_dofus_tweets(self) -> None:
        channel: discord.TextChannel | None = cast(discord.TextChannel | None, self.bot.get_channel(self.TWITTER_FEED))

        if not channel:
            LOGGER.warning("Could not find or access the Dofus Twittter Feed Channel...")
            return

        query = "from:DOFUS_EN -is:reply"
        data: dict[str, Any] = await self.tclient.search_recent_tweets(  # type: ignore
            query,
            max_results=10,
            since_id=self.last_id,
            media_fields=["url"],
            user_auth=False,
            user_fields=["username", "profile_image_url"],
            tweet_fields=["created_at", "attachments"],
            expansions=["author_id", "attachments.media_keys"],
        )

        try:
            meta: dict[str, Any] = data["meta"]
            last_id: int = int(meta["newest_id"])
        except KeyError:
            return

        config = core.CONFIG
        config["TWITTER"]["last_id"] = last_id

        includes = data["includes"]
        media = includes.get("media", [])
        user = includes["users"][0]
        thumb = "https://pbs.twimg.com/profile_images/1863965228213456896/p3BS-OFK.jpg"
        name = user["username"]

        embeds: list[discord.Embed] = []
        for tweet in reversed(data["data"]):
            image: str | None = None
            key = tweet.get("attachments", {}).get("media_keys", [0])[0]

            for d in media:
                if d["media_key"] == key and d["type"] == "photo":
                    image = d["url"]

            embeds.append(self.build_embed(tweet, thumb=thumb, username=name, image=image))

        await channel.send(embeds=embeds)

        with open("config.json", "w+") as fp:
            json.dump(config, fp)

    @fetch_dofus_tweets.before_loop
    async def dofus_tweets_before(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Twitter(bot))
