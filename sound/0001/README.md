🔊 Hybrid SFX Generator

Тестовый прототип гибридного генератора звуковых эффектов (SFX) для видеоигр.
Архитектура: FastAPI backend + минимальный Web UI + AI-модель (AudioLDM) + процедурный DSP-слой.

## Требования

- NVIDIA Driver
- NVIDIA Container Toolkit
- Docker
- Docker Compose

## Запуск

```bash
# Сборка образа
./build.sh

# Запуск контейнера
./up.sh
```

## Веб-интерфейс

Откройте в браузере: http://localhost:8000

## Примечание

При первом запуске происходит скачивание моделей HuggingFace (~2.5 ГБ) в `hf_cache`.