# RPBot

This project contains a simple chat bot implementation with API and optional Telegram interface. A lightweight WebUI inspired by ChatGPT is provided via FastAPI.

## Running the Web UI

Install dependencies and start the server:

```bash
pip install -r rpbot_pkg/requirements.txt
python -m rpbot_pkg.webui.main
```

Open your browser at [http://localhost:8000](http://localhost:8000) to chat with the bot.

The API endpoints remain under `/api`:

- `POST /api/chat/{user_id}` – send a message
- `POST /api/chat/{user_id}/image` – attach an image

## Package Layout

```
rpbot_pkg/
  api/            # API wrappers and request builders
  services/       # Service layer
  bot/            # Telegram bot interface
  webui/          # FastAPI web interface
```
