import asyncio
from telegram import Update, Message, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, MessageHandler, filters, ContextTypes

import config

SOURCE_CHANNEL_ID = config.SOURCE_CHANNEL_ID
TARGET_CHANNEL_ID = config.TARGET_CHANNEL_ID
BOT_TOKEN = config.BOT_TOKEN
KEYWORD = config.KEYWORD

message_mapping = {}
album_messages = {}

def _msg_key(msg: Message):
    return (msg.chat_id, msg.message_id)

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            await handle_new_message(update.message, context)
        elif update.channel_post:
            await handle_new_message(update.channel_post, context)
        if update.edited_message:
            await handle_edited_message(update.edited_message, context)
        elif update.edited_channel_post:
            await handle_edited_message(update.edited_channel_post, context)

    except Exception as e:
        print("error:", e)

async def handle_album_message(media_group_id: str, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(config.ALBUM_DELAY_SECONDS)
    
    if media_group_id not in album_messages:
        return
    
    messages = album_messages[media_group_id]
    if len(messages) < 2:
        if messages:
            msg = messages[0]
            await handle_single_message(msg, context)
        del album_messages[media_group_id]
        return
    messages.sort(key=lambda x: x.message_id)
    first_message = messages[0]
    media_list = []
    for i, msg in enumerate(messages):
        if msg.photo:
            if i == 0:
                media_item = InputMediaPhoto(
                    media=msg.photo[-1].file_id,
                    caption=msg.caption or None
                )
            else:
                media_item = InputMediaPhoto(
                    media=msg.photo[-1].file_id
                )
            media_list.append(media_item)
        elif msg.video:
            if i == 0:
                media_item = InputMediaVideo(
                    media=msg.video.file_id,
                    caption=msg.caption or None
                )
            else:
                media_item = InputMediaVideo(
                    media=msg.video.file_id
                )
            media_list.append(media_item)
    
    if not media_list:
        return
    
    try:
        print(f"Sending album with {len(media_list)} media items...")
        sent_messages = await context.bot.send_media_group(
            chat_id=TARGET_CHANNEL_ID,
            media=media_list
        )
        
        if sent_messages:
            main_target_key = (TARGET_CHANNEL_ID, sent_messages[0].message_id)
            for msg in messages:
                source_key = _msg_key(msg)
                message_mapping[source_key] = main_target_key
                print(f"Album forwarded: {source_key} -> {main_target_key}")
            
            print(f"Successfully sent album with {len(sent_messages)} messages")
        del album_messages[media_group_id]
        
    except Exception as e:
        print(f"Error handling album: {e}")
        print("Falling back to individual forwarding...")
        for msg in messages:
            await handle_single_message(msg, context)
        del album_messages[media_group_id]

async def handle_single_message(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """Обработка одиночного сообщения"""
    try:
        forwarded = await context.bot.copy_message(
            chat_id=TARGET_CHANNEL_ID,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_id=message.message_id
        )

        source_key = _msg_key(message)
        target_key = (TARGET_CHANNEL_ID, forwarded.message_id)
        message_mapping[source_key] = target_key
        print("Single message forwarded:", source_key, "->", target_key)
        
    except Exception as e:
        print(f"Error forwarding single message: {e}")

async def handle_new_message(message: Message, context: ContextTypes.DEFAULT_TYPE):
    if message.chat_id != SOURCE_CHANNEL_ID:
        return

    source_key = _msg_key(message)
    print("NEW:", source_key, f"(media_group: {getattr(message, 'media_group_id', None)})")
    if hasattr(message, 'media_group_id') and message.media_group_id:
        media_group_id = message.media_group_id
        
        if media_group_id not in album_messages:
            album_messages[media_group_id] = []
            asyncio.create_task(handle_album_message(media_group_id, context))
            print(f"Started processing album: {media_group_id}")
        
        album_messages[media_group_id].append(message)
        print(f"Added to album {media_group_id}, total: {len(album_messages[media_group_id])}")
        return 
    await handle_single_message(message, context)

async def handle_edited_message(message: Message, context: ContextTypes.DEFAULT_TYPE):
    if message.chat_id != SOURCE_CHANNEL_ID:
        return

    source_key = _msg_key(message)
    text = (message.text or message.caption or "")

    if KEYWORD.lower() in text.lower():
        print("keyword found:", source_key)
        target_key = message_mapping.get(source_key)

        if target_key:
            try:
                await context.bot.delete_message(chat_id=target_key[0], message_id=target_key[1])
                keys_to_delete = [key for key, value in message_mapping.items() if value == target_key]
                for key in keys_to_delete:
                    del message_mapping[key]
                print(f"Deleted target: {target_key} and {len(keys_to_delete)} mappings")
            except Exception as e:
                print(f"Error deleting message: {e}")
        return
        
    target_key = message_mapping.get(source_key)

    if not target_key:
        print("no mapping for edited message:", source_key)
        return

    new_text = message.text or message.caption or ""

    try:
        if message.text:
            await context.bot.edit_message_text(
                chat_id=target_key[0],
                message_id=target_key[1],
                text=new_text
            )
        else:
            await context.bot.edit_message_caption(
                chat_id=target_key[0],
                message_id=target_key[1],
                caption=new_text
            )
        print("Message edited:", source_key)
    except Exception as e:
        print("edit error:", e)

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_all_messages))

    print("BOT STARTED - Ready to forward messages")
    print("Source channel:", SOURCE_CHANNEL_ID)
    print("Target channel:", TARGET_CHANNEL_ID)
    
    app.run_polling(drop_pending_updates=True)