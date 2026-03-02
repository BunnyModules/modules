# ---------------------------------------------------------------------------------
# ██████  ██    ██ ███    ██ ███    ██ ██    ██ ███    ███  ██████  ██████  ██    ██ ██      ███████ ███████
# ██   ██ ██    ██ ████   ██ ████   ██  ██  ██  ████  ████ ██    ██ ██   ██ ██    ██ ██      ██      ██
# ██████  ██    ██ ██ ██  ██ ██ ██  ██   ████   ██ ████ ██ ██    ██ ██   ██ ██    ██ ██      █████   ███████
# ██   ██ ██    ██ ██  ██ ██ ██  ██ ██    ██    ██  ██  ██ ██    ██ ██   ██ ██    ██ ██      ██           ██
# ██████   ██████  ██   ████ ██   ████    ██    ██      ██  ██████  ██████   ██████  ███████ ███████ ███████
#
# Name: ImageQuoter
# Description: Quote an image
# ---------------------------------------------------------------------------------
# 🔒    Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# ---------------------------------------------------------------------------------
# Author: @BunnyModules
# Commands: away
# scope: hikka_only
# meta developer: @BunnyModules
# ---------------------------------------------------------------------------------

import aiohttp
from .. import loader, utils

@loader.tds
class ImageQuoterMod(loader.Module):
    strings = {
        "name": "ImageQuoter",
        "no_reply": "❌ Reply to a photo!",
        "upload_start": "📤 Uploading to Catbox...",
        "upload_fail": "❌ Upload failed!",
        "result": "📸 Here’s your image link:\n{}"
    }
    strings_en = strings
    strings_ru = {
        "name": "ImageQuoter",
        "no_reply": "❌ Ответь на изображение!",
        "upload_start": "📤 Загружаю на Catbox...",
        "upload_fail": "❌ Загрузка не удалась!",
        "result": "📸 Ссылка на изображение:\n{}"
    }

    async def qi_cmd(self, message):
        """
        .qi
        Reply to an image to upload it and get a preview link.
        """
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings["no_reply"])
            return

        media = reply.media
        if not media:
            await utils.answer(message, self.strings["no_reply"])
            return

        await utils.answer(message, self.strings["upload_start"])
        file_bytes = await message.client.download_media(media, bytes)

        try:
            catbox_url = await self.upload_to_catbox(file_bytes)
        except Exception as e:
            await utils.answer(message, f"{self.strings['upload_fail']}\n{e}")
            return

        await utils.answer(message, self.strings["result"].format(catbox_url))

        async def upload_to_catbox(self, file_bytes: bytes) -> str:
            url = "https://catbox.moe/user/api.php"

            form = aiohttp.FormData()
            form.add_field("reqtype", "fileupload")
            form.add_field("fileToUpload", file_bytes, filename="image.png", content_type="image/png")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    text = await resp.text()
                    return text.strip()
