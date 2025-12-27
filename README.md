# Telegram Autoforwarder

**Original Author:** [Redian Marku](https://github.com/redianmarku/Telegram-Autoforwarder)  
**License:** MIT

## Enhanced Features

This fork adds production-ready enhancements:

- ✅ **Environment variable configuration** - No hardcoded credentials
- ✅ **Multiple source chats** - Forward from unlimited sources simultaneously
- ✅ **Working modes** - Interactive (setup) and Process (production)
- ✅ **Docker support** - Run as containerized service with auto-restart
- ✅ **Session persistence** - Authenticate once, run forever
- ✅ **User/Group/Channel support** - Works with all Telegram entity types

## Quick Start (Docker)

1. **First-time setup** (authenticate):
   ```bash
   # Interactive mode to create session file
   WORKING_MODE=interactive python TelegramForwarder.py
   # Choose option 1 to list chats and get IDs
   ```

2. **Configure environment**:
   ```bash
   # Create .env file
   cat > .env << EOF
   WORKING_MODE=process
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=+1234567890
   TELEGRAM_SOURCE_IDS=-1001234567890,-1009876543210
   TELEGRAM_DEST_ID=-1001122334455
   TELEGRAM_KEYWORDS=
   EOF
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d telegram-forwarder
   docker-compose logs -f telegram-forwarder
   ```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `WORKING_MODE` | `interactive` or `process` | `process` |
| `TELEGRAM_API_ID` | Telegram API ID | `12345678` |
| `TELEGRAM_API_HASH` | Telegram API Hash | `abc123...` |
| `TELEGRAM_PHONE` | Phone number with country code | `+5583981960846` |
| `TELEGRAM_SOURCE_IDS` | Comma-separated source chat IDs | `-1001,8298050989` |
| `TELEGRAM_DEST_ID` | Destination chat ID | `-5119486151` |
| `TELEGRAM_KEYWORDS` | Filter keywords (empty = forward all) | `promo,deal` |

### Getting Chat IDs

Run in interactive mode:
```bash
python TelegramForwarder.py
# Choose option 1: List Chats
# Copy the Chat IDs you need
```

## Manual Setup (Without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables or create `.env` file

3. Run:
   ```bash
   python TelegramForwarder.py
   ```

## How It Works

- Uses Telethon library for Telegram API
- Polls source chats every 5 seconds for new messages
- Forwards messages matching keywords (or all if no keywords)
- Session file persists authentication
- Works with Users, Groups, and Channels

## Notes

- Get API credentials from [my.telegram.org](https://my.telegram.org)
- Session file (`session_*.session`) must be preserved
- Requires read permissions in source chats
- Requires write permissions in destination chat
- Keywords are case-insensitive
