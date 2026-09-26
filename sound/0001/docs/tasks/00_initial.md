Ниже — готовый, структурированный промпт для Cline-агента. Скопируйте его целиком и отправьте агенту, указав целевую папку.

---

## 📋 Задача для Cline-агента: Создание Docker-прототипа Hybrid SFX Generator

### 🎯 Контекст
Ты создаёшь тестовый прототип гибридного генератора звуковых эффектов (SFX) для видеоигр. Архитектура: FastAPI backend + минимальный Web UI + AI-модель (AudioLDM как заглушка вместо TangoFlux) + процедурный DSP-слой. Всё упаковано в Docker-контейнер с поддержкой GPU (NVIDIA).

### 📁 Целевая директория
Все файлы должны быть созданы в папке: `./sfx-generator/` (создай её, если не существует).

### ⛔ КРИТИЧЕСКОЕ ОГРАНИЧЕНИЕ
**КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** использовать любые инструменты для выполнения команд в терминале (`execute_command`, `run_shell`, `bash`, `docker build`, `docker-compose up` и т.д.). 
Твоя задача — **ТОЛЬКО создать файлы** с помощью инструментов создания/редактирования файлов. Пользователь сам запустит сборку и запуск вручную.

---

### 📂 Структура проекта и содержимое файлов

Создай следующие файлы с указанным содержимым:

#### 1. `sfx-generator/requirements.txt`
Python-зависимости проекта:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
jinja2==3.1.3
torch==2.1.2
torchaudio==2.1.2
diffusers==0.26.1
transformers==4.37.1
accelerate==0.26.1
librosa==0.10.1
soundfile==0.12.1
numpy==1.26.3
scipy==1.12.0
```

#### 2. `sfx-generator/app/__init__.py`
Пустой файл (инициализатор пакета).

#### 3. `sfx-generator/app/generator.py`
Класс `SFXGenerator` с методами:
- `__init__`: определяет device (cuda/cpu).
- `load_model`: загружает `AudioLDMPipeline` из `cvssp/audioldm` в `float16`, применяет `enable_model_cpu_offload()` и `enable_attention_slicing()` для экономии VRAM (под 3 ГБ).
- `generate_dsp_boom(duration, sr)`: генерирует процедурный низкочастотный бум через NumPy (sine sweep + exponential decay).
- `generate(prompt)`: генерирует AI-слой через пайплайн, DSP-слой, микширует их (AI × 0.7 + DSP × 0.5), нормализует до 0.95, сохраняет в `/app/audio_output/sfx_{uuid}.wav` с sample_rate=16000. Возвращает dict `{filename, url, prompt}`.
- Глобальный экземпляр `generator = SFXGenerator()`.

#### 4. `sfx-generator/app/main.py`
FastAPI приложение:
- `startup_event`: предзагружает модель через `generator.load_model()`.
- `GET /`: отдаёт `index.html` через Jinja2Templates.
- `POST /generate`: принимает JSON `{prompt}`, вызывает `generator.generate(prompt)`, возвращает результат.
- `GET /download/{filename}`: отдаёт файл из `OUTPUT_DIR` как `FileResponse`.
- `GET /history`: возвращает список всех `.wav` файлов из `OUTPUT_DIR` (отсортированных по убыванию).
- Запуск через `uvicorn` на `0.0.0.0:8000`.

#### 5. `sfx-generator/app/templates/index.html`
Минимальный UI на Tailwind CSS (через CDN):
- Поле ввода промпта (по умолчанию: "magical fire explosion in a cave").
- Кнопка "Сгенерировать" с индикатором загрузки (спиннер).
- Блок "История генераций": список карточек с тегом `<audio controls>` и кнопкой "Скачать".
- JavaScript: функции `generateSFX()` (POST-запрос) и `loadHistory()` (GET-запрос, рендеринг списка).

#### 6. `sfx-generator/Dockerfile`
```dockerfile
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
RUN mkdir -p /app/audio_output
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7. `sfx-generator/docker-compose.yml`
```yaml
version: '3.8'
services:
  sfx-generator:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./audio_output:/app/audio_output
      - ./hf_cache:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    restart: unless-stopped
```

#### 8. `sfx-generator/build.sh` (в корне репозитория)
Bash-скрипт для пересборки образа:
```bash
#!/bin/bash
set -e
echo "🔨 Building SFX Generator Docker image..."
docker-compose build --no-cache
echo "✅ Build completed successfully!"
```
**Обязательно** сделай скрипт исполняемым (если агент поддерживает установку прав, иначе укажи в комментарии, что пользователь должен выполнить `chmod +x build.sh`).

#### 9. `sfx-generator/up.sh` (в корне репозитория)
Bash-скрипт для пересоздания и запуска контейнера:
```bash
#!/bin/bash
set -e
echo "🚀 Stopping existing containers..."
docker-compose down || true
echo "📦 Starting SFX Generator..."
docker-compose up -d --build
echo "✅ Container is running at http://localhost:8000"
echo "📋 Logs:"
docker-compose logs -f
```

#### 10. `sfx-generator/README.md`
Краткая инструкция:
- Описание проекта.
- Требования (NVIDIA Driver, NVIDIA Container Toolkit, Docker, Docker Compose).
- Команды запуска: `./build.sh` и `./up.sh`.
- URL веб-интерфейса: `http://localhost:8000`.
- Примечание о первом запуске (скачивание моделей ~2.5 ГБ в `hf_cache`).

---

### ✅ Критерии проверки (Definition of Done)

Задача считается выполненной, если:

1. **Структура файлов**: Созданы все 10 файлов по указанным путям. Иерархия папок (`app/`, `app/templates/`) соблюдена.
2. **Корректность Python-кода**:
   - `generator.py` использует `torch.float16` и `enable_model_cpu_offload()`.
   - `main.py` содержит все 4 эндпоинта (`/`, `/generate`, `/download/{filename}`, `/history`).
   - Импорты корректны, нет синтаксических ошибок.
3. **Корректность Docker-конфигурации**:
   - `Dockerfile` основан на `pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime`.
   - `docker-compose.yml` содержит проброс GPU через `deploy.resources.reservations.devices`.
   - Проброшены два volume: `./audio_output` и `./hf_cache`.
4. **Скрипты `build.sh` и `up.sh`**:
   - Находятся строго в корне `sfx-generator/`.
   - Содержат shebang `#!/bin/bash` и `set -e`.
   - `build.sh` вызывает `docker-compose build`.
   - `up.sh` вызывает `docker-compose down`, затем `docker-compose up -d --build`, затем `docker-compose logs -f`.
5. **UI**:
   - `index.html` использует Tailwind через CDN.
   - Содержит поле ввода, кнопку генерации, спиннер загрузки, блок истории с `<audio>` тегами и кнопками скачивания.
6. **Ограничение соблюдено**: Агент **НЕ выполнил** ни одной команды в терминале. Все действия — только создание/редактирование файлов.

---

### 🚀 Начало работы
Начни с создания структуры папок и файла `requirements.txt`, затем переходи к Python-коду, Docker-конфигурации и в конце — к bash-скриптам и README. После создания каждого файла кратко подтверждай его путь.