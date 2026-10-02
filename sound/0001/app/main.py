import os
import glob
import logging
import time
import traceback
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.generator import generator

# Настраиваем логгер для FastAPI
logger = logging.getLogger("sfx-generator-api")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
    logger.info("=" * 60)
    logger.info("🚀 SFX Generator API starting up...")
    logger.info("=" * 60)
    generator.load_model()
    logger.info("✅ Model loaded, API ready to serve requests")
    logger.info("=" * 60)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с UI."""
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/generate")
async def generate_sfx(req: GenerateRequest):
    """Эндпоинт для генерации звукового эффекта."""
    request_id = str(__import__('uuid').uuid4())[:8]
    start_time = time.time()
    
    logger.info(f"[{request_id}] 📨 NEW REQUEST: prompt='{req.prompt}'")
    
    try:
        logger.debug(f"[{request_id}] Calling generator.generate()...")
        result = generator.generate(req.prompt)
        elapsed = time.time() - start_time
        
        logger.info(f"[{request_id}] ✅ Request completed successfully in {elapsed:.2f}s")
        logger.info(f"[{request_id}]    Response: filename={result.get('filename', 'N/A')}, url={result.get('url', 'N/A')}")
        
        return result
        
    except torch.cuda.OutOfMemoryError as e:
        elapsed = time.time() - start_time
        logger.error(f"[{request_id}] ❌ CUDA OOM after {elapsed:.2f}s: {e}")
        raise HTTPException(status_code=503, detail="GPU out of memory. Try again later.")
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[{request_id}] ❌ Request failed after {elapsed:.2f}s: {e}")
        logger.debug(f"[{request_id}] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


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