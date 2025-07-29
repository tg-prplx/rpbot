from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from rpbot_pkg.services.chat_service import ChatService


BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="RP Pollinations Bot WebUI")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

chat_sessions = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat/{user_id}")
async def api_chat(user_id: int, data: dict):
    message = data.get("message", "")
    state = chat_sessions.setdefault(
        user_id,
        {"chat": ChatService(model="deepseek-ai/DeepSeek-V3", stream=False, max_tokens=200000), "history": []},
    )
    resp, prompt = await state["chat"].handle_message(message)
    state["history"].append((message, resp))
    return {"response": resp, "image_prompt": prompt}


@app.post("/api/chat/{user_id}/image")
async def add_image(user_id: int, file: UploadFile = File(...), caption: str = ""):
    state = chat_sessions.setdefault(
        user_id,
        {"chat": ChatService(model="deepseek-ai/DeepSeek-V3", stream=False, max_tokens=200000), "history": []},
    )
    path = Path("/tmp") / file.filename
    content = await file.read()
    path.write_bytes(content)
    try:
        await state["chat"].handle_image_message(str(path), caption)
    finally:
        path.unlink(missing_ok=True)
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

