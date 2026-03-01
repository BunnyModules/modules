# ---------------------------------------------------------------------------------
# ██████  ██    ██ ███    ██ ███    ██ ██    ██ ███    ███  ██████  ██████  ██    ██ ██      ███████ ███████
# ██   ██ ██    ██ ████   ██ ████   ██  ██  ██  ████  ████ ██    ██ ██   ██ ██    ██ ██      ██      ██
# ██████  ██    ██ ██ ██  ██ ██ ██  ██   ████   ██ ████ ██ ██    ██ ██   ██ ██    ██ ██      █████   ███████
# ██   ██ ██    ██ ██  ██ ██ ██  ██ ██    ██    ██  ██  ██ ██    ██ ██   ██ ██    ██ ██      ██           ██
# ██████   ██████  ██   ████ ██   ████    ██    ██      ██  ██████  ██████   ██████  ███████ ███████ ███████
#
# Name: Away
# Description: Send a message when you're offline
# ---------------------------------------------------------------------------------
# 🔒    Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# ---------------------------------------------------------------------------------
# Author: @BunnyModules
# Commands: away
# scope: hikka_only
# meta developer: @BunnyModules
# ---------------------------------------------------------------------------------

from telethon.tl.types import (
    UserStatusOffline,
    UserStatusLastWeek,
    UserStatusLastMonth,
)
from .. import loader, utils


@loader.tds
class Away(loader.Module):
    strings = {
        "name": "Away",
        "on": "🟢 <b>Away enabled</b>",
        "off": "🔴 <b>Away disabled</b>",
    }

    strings_ru = {
        "name": "Away",
        "on": "🟢 <b>Away включён</b>",
        "off": "🔴 <b>Away выключен</b>",
    }

    strings_en = {
        "name": "Away",
        "on": "🟢 <b>Away enabled</b>",
        "off": "🔴 <b>Away disabled</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "reply_dm",
                True,
                "Auto-reply in private messages",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "reply_reply",
                True,
                "Auto-reply to replies in groups/channels",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "message",
                "I'm offline right now. Last seen: %s.",
                "Auto-reply message (%s = last seen)",
                validator=loader.validators.String(),
            ),
        )

        self.away = False
        self._replied = set()
        self._me_id = None

    async def client_ready(self, client, db):
        self._client = client
        self._me_id = (await client.get_me()).id

    @loader.command(name="away")
    async def awaycmd(self, message):
        self.away = not self.away
        self._replied.clear()

        await utils.answer(
            message,
            self.strings("on") if self.away else self.strings("off"),
        )

    async def _last_seen(self):
        me = await self._client.get_me()
        status = me.status

        if isinstance(status, UserStatusOffline):
            return status.was_online.strftime("%d.%m.%Y %H:%M")
        if isinstance(status, UserStatusLastWeek):
            return "last week"
        if isinstance(status, UserStatusLastMonth):
            return "a long time ago"

        return "just now"

    @loader.watcher()
    async def watcher(self, message):
        if not self.away:
            return

        if message.out or not message.sender_id:
            return

        key = (message.chat_id, message.sender_id)
        if key in self._replied:
            return

        last = await self._last_seen()
        text = self.config["message"].replace("%s", last)

        if message.is_private and self.config["reply_dm"]:
            await message.reply(text)
            self._replied.add(key)
            return

        if self.config["reply_reply"] and message.reply_to:
            reply = await message.get_reply_message()
            if reply and reply.sender_id == self._me_id:
                await message.reply(text)
                self._replied.add(key)
