

# RPBot (Roleplay & Art Generation Telegram Bot)

**RPBot** is a Telegram bot powered by language models (LLM) and AI art generation. You can chat, change the bot's behavior, and generate unique images directly in the chat!

---

## ✨ Features

- 🤖 Conversational AI with LLM (ChatGPT-compatible)
- 🖼️ Text-to-image generation
- 👤 Customizable character/personality and appearance of the bot
- 💬 Persistent dialogue history and user statistics
- 🕹️ Simple command interface
- ⚡ Built with Python, aiohttp, tiktoken, OpenAI API
- 📷 Receive images directly in Telegram

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/tg-prplx/rpbot.git
cd rpbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables  
Create a `.env` file or add your tokens and API keys directly.

```env
TELEGRAM_BOT_TOKEN=your_telegram_token
```

### 4. Run the bot

```bash
python rp_pollinations_bot.py
```

---

## 🛠️ Commands

- `/setcharacter` — Set the bot’s character or appearance  
- `/reset` — Reset the chat and start over  
- `/history` — Show the last 5 messages  
- `/repeat` — Repeat the last reply  
- `/stats` — Show chat statistics  
- `/help` — Show help and commands

---

## 📂 Project Structure

- `rp_pollinations_bot.py` — Main bot code
- `chat_service.py`, `chat.py`, `chat_request_constructor.py` — LLM and conversation logic
- `image_generation_constructor.py` — Image generation (prompt to art)
- `requirements.txt` — Dependencies

---

## ℹ️ About

**Author:** WhyDev (tg-prplx)  
This project is experimental and created for fun and demonstration of what’s possible with LLMs and AI art generation.

---

## 📄 License

MIT License.  
Use at your own risk!

---

**Pull requests and suggestions are very welcome!**
