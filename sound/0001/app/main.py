import os
import glob
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.generator import generator

app = FastAPI(title="Hybrid SFX Generator")

# Templates и static files
templates = Jinja2Templates(directory="/app/app/templates")

# Создаем директорию для вывода если нет
OUTPUT_DIR = "/app/audio_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class GenerateRequest(BaseModel):
    prompt: str


@app.on_event("startup")
async def startup_event():
    """Предзагрузка модели при старте приложения."""
    generator.load_model()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с UI."""
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/generate")
async def generate_sfx(req: GenerateRequest):
    """Эндпоинт для генерации звукового эффекта."""
    try:
        result = generator.generate(req.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_sfx(filename: str):
    """Эндпоинт для скачивания сгенерированного файла."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="audio/wav", filename=filename)


@app.get("/history")
async def get_history():
    """Возвращает список всех .wav файлов из OUTPUT_DIR (по убыванию даты)."""
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.wav"))
    files.sort(key=os.path.getmtime, reverse=True)
    
    result = []
    for f in files:
        filename = os.path.basename(f)
        result.append({
            "filename": filename,
            "url": f"/download/{filename}"
        })
    
    return result