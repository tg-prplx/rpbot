from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.chat_service import ChatService

app = FastAPI(title="RP Pollinations Bot WebUI")
chat_sessions = {}

@app.post("/chat/{user_id}")
async def chat(user_id: int, message: str):
    state = chat_sessions.setdefault(user_id, {
        "chat": ChatService(model="deepseek-ai/DeepSeek-V3", stream=False, max_tokens=200000),
        "history": []
    })
    resp, prompt = await state["chat"].handle_message(message)
    state["history"].append((message, resp))
    return {"response": resp, "image_prompt": prompt}

@app.post("/chat/{user_id}/image")
async def add_image(user_id: int, file: UploadFile = File(...), caption: str = ""):
    state = chat_sessions.setdefault(user_id, {
        "chat": ChatService(model="deepseek-ai/DeepSeek-V3", stream=False, max_tokens=200000),
        "history": []
    })
    path = Path("/tmp")/file.filename
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

