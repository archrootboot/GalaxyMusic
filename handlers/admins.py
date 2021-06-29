# Calls Music 1 - Telegram bot for streaming audio in group calls
# Copyright (C) 2021  Roj Serbest

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from asyncio.queues import QueueEmpty
from cache.admins import set
from pyrogram import Client
from pyrogram.types import Message
from callsmusic import callsmusic
import traceback
import os
import sys
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram import filters, emoji
from config import BOT_NAME as BN
from helpers.filters import command, other_filters
from helpers.decorators import errors, authorized_users_only
from config import que, admins as a

@Client.on_message(filters.command('adminreset'))
async def update_admin(client, message):
    global a
    admins = await client.get_chat_members(message.chat.id, filter="administrators")
    new_ads = []
    for u in admins:
        new_ads.append(u.user.id)
    a[message.chat.id] = new_ads
    await message.reply_text('𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙪𝙥𝙙𝙖𝙩𝙚𝙙 𝙖𝙙𝙢𝙞𝙣 𝙡𝙞𝙨𝙩 𝙞𝙣 **{}**'.format(message.chat.title))




@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == 'paused'
    ):
        await message.reply_text("𝙉𝙤𝙩𝙝𝙞𝙣𝙜 𝙞𝙨 𝙥𝙡𝙖𝙮𝙞𝙣𝙜!🤪")
    else:
        callsmusic.pytgcalls.pause_stream(message.chat.id)
        await message.reply_text("𝙋𝙖𝙪𝙨𝙚𝙙! ▶️")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == 'playing'
    ):
        await message.reply_text("𝙉𝙤𝙩𝙝𝙞𝙣𝙜 𝙞𝙨 𝙥𝙖𝙪𝙨𝙚𝙙! 🤪 ")
    else:
        callsmusic.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text("𝙍𝙚𝙨𝙪𝙢𝙚𝙙! ⏸")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("𝙉𝙤𝙩𝙝𝙞𝙣𝙜 𝙞𝙨 𝙨𝙩𝙧𝙚𝙖𝙢𝙞𝙣𝙜! 🤪")
    else:
        try:
            callsmusic.queues.clear(message.chat.id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text("❌ 𝙎𝙩𝙤𝙥𝙥𝙚𝙙 𝙨𝙩𝙧𝙚𝙖𝙢𝙞𝙣𝙜!")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("𝙉𝙤𝙩𝙝𝙞𝙣𝙜 𝙞𝙨 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙩𝙤 𝙨𝙠𝙞𝙥!🤪")
    else:
        callsmusic.queues.task_done(message.chat.id)

        if callsmusic.queues.is_empty(message.chat.id):
            callsmusic.pytgcalls.leave_group_call(message.chat.id)
        else:
            callsmusic.pytgcalls.change_stream(
                message.chat.id,
                callsmusic.queues.get(message.chat.id)["file"]
            )
                

    qeue = que.get(message.chat.id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f'- 𝙎𝙠𝙞𝙥𝙥𝙚𝙙 **{skip[0]}**\n-𝙉𝙤𝙬 𝙋𝙡𝙖𝙮𝙞𝙣𝙜 ••• **{qeue[0][0]}**')


@Client.on_message(
    filters.command("reload")
)
@errors
async def reload(client, message: Message):
    set(message.chat.id, [member.user for member in await message.chat.get_members(filter="administrators")])
    await message.reply_text("✯ 𝙑𝙤𝙞𝙘𝙚𝘾𝙝𝙖𝙩 𝙋𝙡𝙖𝙮𝘽𝙤𝙩 ✯=❇️ 𝘼𝙙𝙢𝙞𝙣 𝙘𝙖𝙘𝙝𝙚 𝙧𝙚𝙛𝙧𝙚𝙨𝙝𝙚𝙙!")
