import asyncio

from pyrogram import *
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils import get_readable_time
from AnonXMusic.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
    is_gdel_user,
    get_gdel_user, get_gdel_count,
    add_gdel_user, del_gdel_user
)
from AnonXMusic.utils.decorators.language import language
from AnonXMusic.utils.extraction import extract_user
from config import BANNED_USERS


@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
@language
async def global_ban(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user.id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user.id in SUDOERS:
        return await message.reply_text(_["gban_3"])
    is_gbanned = await is_banned_user(user.id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(user.mention))
    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_5"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue
    await add_banned_user(user.id)
    await message.reply_text(
        _["gban_6"].format(
            app.mention,
            message.chat.title,
            message.chat.id,
            user.mention,
            user.id,
            message.from_user.mention,
            number_of_chats,
        )
    )
    await mystic.delete()


@app.on_message(filters.command(["ungban"]) & SUDOERS)
@language
async def global_un(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    is_gbanned = await is_banned_user(user.id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(user.mention))
    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_8"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue
    await remove_banned_user(user.id)
    await message.reply_text(_["gban_9"].format(user.mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])
    mystic = await message.reply_text(_["gban_11"])
    msg = _["gban_12"]
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ {user_id}\n"
            continue
    if count == 0:
        return await mystic.edit_text(_["gban_10"])
    else:
        return await mystic.edit_text(msg)


@app.on_message(commandx(["gdl", "gdel", "gdelete"]) & SUDOERS)
async def add_gdelete_user(client, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("Reply to a user's message or give username/user_id.")
        user = message.text.split(None, 1)[1]
        user = await app.get_users(user)
        user_id = user.id
        mention = user.mention
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    if user_id == message.from_user.id:
        return await message.reply_text("You want to add Global Delete yourself? How Fool!")
    elif user_id == SUPUSER:
        return await message.reply_text("Should i activate Global Delete on myself? Lol")
    elif user_id in SUDOERS:
        return await message.reply_text("You want add Global Delete on sudo user?")
    is_gdel = await is_gdel_user(user_id)
    if is_gdel:
        return await message.reply_text("{0} is already affected by **Global Delete**".format(mention))
    if user_id not in GDELSUB:
        GDELSUB.add(user_id)
    await add_gdel_user(user_id)
    await message.reply_text("**Global Delete Activated.")



@app.on_message(commandx(["ungdl", "ungdel", "ungdelete"]) & SUDOERS)
async def del_gdelete_user(client, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("Reply to a user's message or give username/user_id.")
        user = message.text.split(None, 1)[1]
        user = await app.get_users(user)
        user_id = user.id
        mention = user.mention
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    is_gdel = await is_gdel_user(user_id)
    if not is_gdel:
        return await message.reply_text("{0} is not affected by Global Delete.".format(mention))
    if user_id in GDELSUB:
        GDELSUB.remove(user_id)
    await del_gdel_user(user_id)
    await message.reply_text("De-Activated Global Delete On {0}".format(mention)
    )



@app.on_message(commandx(["gdlst", "gdellist", "gdelusers"]) & SUDOERS)
async def gdelete_users_list(client, message: Message):
    counts = await get_gdel_count()
    if counts == 0:
        return await message.reply_text("No Global Delete Users Found.")
    txt = await message.reply_text("Please wait a while.. Fetching Global Delete users list")
    msg = "Global Delete Users:\n\n"
    count = 0
    users = await get_gdel_user()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = (
                user.first_name if not user.mention else user.mention
            )
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ [Unfetched User]{user_id}\n"
            continue
    if count == 0:
        return await txt.edit_text("No Global Delete Users Found.")
    else:
        return await txt.edit_text(msg)
