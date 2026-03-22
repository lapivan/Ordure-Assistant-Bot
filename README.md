# Ordure-Assistant-Bot

A Telegram bot that forwards messages from one channel to another, synchronizes edits, supports albums, and automatically deletes forwarded messages when a keyword appears in the original message.

---

## Features

- Forward text messages  
- Forward photos and videos (including albums)  
- Sync edits (text and captions)  
- Auto-delete when a keyword appears  
- Album support with delay handling  

---

## Requirements

- Python 3.8+ (recommended)
- A Telegram Bot token (from BotFather)
- Bot must be an administrator in both channels

### Required permissions:

**Source channel:**
- Read messages

**Target channel:**
- Post messages
- Delete messages
- Edit messages

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/lapivan/Ordure-Assistant-Bot.git
cd Ordure-Assistant-Bot
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

---

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

---

### 4. Upgrade pip (recommended)

```bash
python -m pip install --upgrade pip
```

---

### 5. Install dependencies

```bash
pip install python-telegram-bot==20.*
```

---

## Project structure

```
Ordure-Assistant-Bot/
│
├── bot.py
├── config.py
└── README.md
```

---

## Configuration

Create a `config.py` file in the root directory:

```python
BOT_TOKEN = "your_bot_token_here"

SOURCE_CHANNEL_ID = someid
TARGET_CHANNEL_ID = someid

KEYWORD = "your keyword"

ALBUM_DELAY_SECONDS = 2.0
```

## How it works

1. Bot listens to all messages in the source channel  
2. Messages are copied to the target channel  
3. Albums are grouped and sent together  
4. Message mappings are stored in memory  
5. When a message is edited:
   - If it contains the keyword → forwarded message is deleted  
   - Otherwise → forwarded message is updated  

---

## Run the bot

```bash
python bot.py
```

---

## Important notes

- The bot uses `copy_message`, not forward (no "forwarded from" label)
- Albums are delayed using `ALBUM_DELAY_SECONDS`
- All mappings are stored in memory (restart will reset them)
- If messages are not syncing:
  - Check bot permissions
  - Verify channel IDs
  - Ensure bot is admin

---

## Troubleshooting

### Bot does not receive messages
- Make sure it is admin in the source channel
- Disable privacy mode via BotFather

### Messages are not deleted
- Check delete permission in target channel
- Verify KEYWORD value

### Albums are broken
- Increase ALBUM_DELAY_SECONDS (e.g. 3–5 seconds)

---
