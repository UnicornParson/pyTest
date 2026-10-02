import os
import uuid
import logging
import traceback
import numpy as np
import soundfile as sf
from diffusers import AudioLDMPipeline
import torch
from transformers import AutoFeatureExtractor

from pathlib import Path

# Настраиваем логгер
logger = logging.getLogger("sfx-generator")
logger.setLevel(logging.DEBUG)
# Добавляем handler если его нет (для Docker вывода)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

OUTPUT_DIR = Path("/app/audio_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class SFXGenerator:
    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model_loaded = False
        logger.info(f"🚀 SFX Generator initialized. Using device: {self.device}")
        logger.debug(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.debug(f"CUDA device count: {torch.cuda.device_count()}")
            logger.debug(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"🚀 SFX Generator initialized. Using device: {self.device}")

    def load_model(self):
        """Загружает AudioLDM модель с подробным логгированием."""
        if self.pipe is not None:
            logger.debug("Model already loaded, skipping")
            return
        
        logger.info("⏳ Starting model loading process...")
        logger.info(f"Device: {self.device}")
        logger.debug(f"torch.version: {torch.__version__}")
        
        try:
            logger.info("Downloading/loading AudioLDM pipeline from cvssp/audioldm...")
            # Загружаем ТОЛЬКО пайплайн. Он сам подтянет UNet, VAE и Vocoder.
            self.pipe = AudioLDMPipeline.from_pretrained(
                "cvssp/audioldm", 
                torch_dtype=torch.float16
            )
            logger.debug("Pipeline loaded from pretrained model")
            
            if self.device == "cuda":
                logger.info("Enabling CUDA optimizations...")
                # Включаем оффлоад для экономии VRAM (критично для 3GB карт)
                self.pipe.enable_model_cpu_offload()
                logger.debug("Model CPU offload enabled")
                self.pipe.enable_attention_slicing()
                logger.debug("Attention slicing enabled")
                
                # Проверяем доступный VRAM
                if torch.cuda.is_available():
                    allocated = torch.cuda.memory_allocated() / 1024**3
                    reserved = torch.cuda.memory_reserved() / 1024**3
                    logger.info(f"VRAM after load: allocated={allocated:.2f}GB, reserved={reserved:.2f}GB")
            else:
                logger.info("Moving model to CPU...")
                self.pipe.to(self.device)
                logger.debug("Model moved to CPU")
                
            self._model_loaded = True
            logger.info("✅ Model loaded successfully!")
            
        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"❌ CUDA Out of memory: {e}")
            logger.error("Try reducing batch size or using CPU mode")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise

    def generate_dsp_boom(self, duration=2.5, sr=16000):
        """Процедурный низкочастотный бум (sine sweep + decay)."""
        logger.debug(f"Generating DSP boom: duration={duration}s, sr={sr}")
        try:
            t = np.linspace(0, duration, int(sr * duration), False)
            logger.debug(f"Time array shape: {t.shape}")
            
            freqs = np.linspace(80, 30, len(t))
            logger.debug(f"Frequency range: {freqs[0]:.1f}Hz -> {freqs[-1]:.1f}Hz")
            
            phase = 2 * np.pi * np.cumsum(freqs) / sr
            logger.debug(f"Phase array shape: {phase.shape}")
            
            audio = np.sin(phase) * np.exp(-3.0 * t)
            logger.debug(f"Audio waveform shape before cast: {audio.shape}, dtype: {audio.dtype}")
            
            result = audio.astype(np.float32)
            logger.debug(f"DSP boom generated: length={len(result)} samples, max={np.max(np.abs(result)):.3f}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to generate DSP boom: {e}")
            raise

    def generate(self, prompt: str) -> dict:
        """Генерирует гибридный звуковой эффект (AI + DSP) с подробным логгированием."""
        start_time = __import__('time').time()
        logger.info("=" * 60)
        logger.info(f"🎯 NEW GENERATION REQUEST")
        logger.info(f"   Prompt: '{prompt}'")
        logger.info("=" * 60)
        
        # Проверка модели
        if not self._model_loaded or self.pipe is None:
            logger.info("Model not loaded, loading now...")
            self.load_model()
            logger.info("Model ready")
        
        # Генерация уникального имени
        file_id = str(uuid.uuid4())[:8]
        filename = f"sfx_{file_id}.wav"
        filepath = OUTPUT_DIR / filename
        logger.info(f"📁 Output file: {filepath}")
        
        # ====== ЭТАП 1: AI генерация ======
        logger.info("-" * 40)
        logger.info("🎨 STAGE 1: AI Layer Generation")
        logger.info("-" * 40)
        
        try:
            logger.info(f"Parameters:")
            logger.info(f"  - prompt: '{prompt}'")
            logger.info(f"  - audio_length_in_s: 2.5")
            logger.info(f"  - num_inference_steps: 10")
            logger.info(f"  - guidance_scale: 2.5")
            
            # Проверяем VRAM перед генерацией
            if self.device == "cuda" and torch.cuda.is_available():
                mem_before = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"VRAM before generation: {mem_before:.2f}GB")
            
            logger.info("Starting inference (10 steps)...")
            
            # Генерация AI слоя
            result = self.pipe(
                prompt=prompt,
                audio_length_in_s=2.5,
                num_inference_steps=10,  # 10 шагов для быстрого прототипа
                guidance_scale=2.5,
            )
            
            logger.debug(f"Inference result type: {type(result)}")
            logger.debug(f"Result attributes: {dir(result)}")
            
            if hasattr(result, 'audios'):
                logger.debug(f"result.audios type: {type(result.audios)}")
                logger.debug(f"result.audios length: {len(result.audios)}")
            
            ai_audio = result.audios[0]  # Достаем numpy array из кортежа
            # Если получили скаляр, пытаемся альтернативный формат извлечения
            if np.isscalar(ai_audio) or (isinstance(ai_audio, np.ndarray) and ai_audio.ndim == 0):
                ai_audio = result.audios[0]
                if isinstance(ai_audio, torch.Tensor):
                    ai_audio = ai_audio.cpu().numpy()
                elif isinstance(ai_audio, (list, tuple)) and len(ai_audio) > 0:
                    ai_audio = np.array(ai_audio[0])
            # Убедимся, что это 1D массив
            if isinstance(ai_audio, np.ndarray) and ai_audio.ndim > 1:
                ai_audio = ai_audio.flatten()
            # Если результат остаётся torch.Tensor
            if isinstance(ai_audio, torch.Tensor):
                ai_audio = ai_audio.cpu().numpy().astype(np.float32)
            logger.info(f"✅ AI layer generated successfully")
            logger.info(f"   Type: {type(ai_audio)}")
            logger.info(f"   Shape: {ai_audio.shape if hasattr(ai_audio, 'shape') else 'N/A'}")
            logger.info(f"   Dtype: {ai_audio.dtype if hasattr(ai_audio, 'dtype') else 'N/A'}")
            logger.info(f"   Min: {np.min(ai_audio):.4f}, Max: {np.max(ai_audio):.4f}")
            
            # Проверяем VRAM после генерации
            if self.device == "cuda" and torch.cuda.is_available():
                mem_after = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"VRAM after AI generation: {mem_after:.2f}GB")
            
        except torch.cuda.OutOfMemoryError:
            logger.error("❌ CUDA OOM during AI generation!")
            logger.error("Tips:")
            logger.error("  1. Try reducing audio_length_in_s")
            logger.error("  2. Try reducing num_inference_steps")
            logger.error("  3. Close other GPU-intensive applications")
            raise
        except Exception as e:
            logger.error(f"❌ Failed during AI generation: {e}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise
        
        # ====== ЭТАП 2: DSP генерация ======
        logger.info("-" * 40)
        logger.info("⚙️ STAGE 2: DSP Layer Generation (Boom)")
        logger.info("-" * 40)
        
        dsp_audio = self.generate_dsp_boom(duration=2.5, sr=16000)
        logger.info(f"✅ DSP layer generated: length={len(dsp_audio)}, dtype={dsp_audio.dtype}")
        
        # ====== ЭТАП 3: Микширование ======
        logger.info("-" * 40)
        logger.info("🎛️ STAGE 3: Mixing AI + DSP")
        logger.info("-" * 40)
        
        try:
            min_len = min(len(ai_audio), len(dsp_audio))
            logger.info(f"Mixing lengths: AI={len(ai_audio)}, DSP={len(dsp_audio)}, using={min_len}")
            
            mixed_audio = ai_audio[:min_len] * 0.7 + dsp_audio[:min_len] * 0.5
            logger.info(f"Mixed audio: shape={mixed_audio.shape}, dtype={mixed_audio.dtype}")
            
            # Нормализация
            max_val = np.max(np.abs(mixed_audio))
            logger.info(f"Pre-normalization max value: {max_val:.4f}")
            
            if max_val > 0:
                mixed_audio = mixed_audio / max_val * 0.95
                logger.info(f"Post-normalization max value: {np.max(np.abs(mixed_audio)):.4f}")
            
        except Exception as e:
            logger.error(f"❌ Failed during mixing: {e}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise
        
        # ====== ЭТАП 4: Сохранение ======
        logger.info("-" * 40)
        logger.info("💾 STAGE 4: Saving WAV file")
        logger.info("-" * 40)
        
        try:
            sf.write(filepath, mixed_audio, 16000)
            file_size = filepath.stat().st_size if filepath.exists() else 0
            logger.info(f"✅ File saved successfully: {filepath}")
            logger.info(f"   File size: {file_size} bytes ({file_size/1024:.1f} KB)")
            logger.info(f"   Sample rate: 16000 Hz")
            logger.info(f"   Duration: ~{len(mixed_audio)/16000:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            raise
        
        # ====== ФИНАЛ ======
        elapsed = __import__('time').time() - start_time
        logger.info("=" * 60)
        logger.info(f"✨ GENERATION COMPLETE")
        logger.info(f"   Filename: {filename}")
        logger.info(f"   URL: /download/{filename}")
        logger.info(f"   Total time: {elapsed:.2f}s")
        logger.info("=" * 60)
        
        return {
            "filename": filename,
            "url": f"/download/{filename}",
            "prompt": prompt,
            "generation_time": round(elapsed, 2)
        }



class SFXGenerator_old:
    """Гибридный генератор звуковых эффектов: AI + DSP слой."""

    def __init__(self):
        """Инициализация генератора с определением устройства."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.output_dir = "/app/audio_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_model(self):
        """Загружает AudioLDM модель в float16 с оптимизациями для экономии VRAM."""
        print(f"Loading AudioLDM model on {self.device}...")
        self.feature_extractor = AutoFeatureExtractor.from_pretrained("cvssp/audioldm")
        self.model = AudioLDMPipeline.from_pretrained(
            "cvssp/audioldm",
            torch_dtype=torch.float16
        ).to(self.device)
        
        # Оптимизации для экономии VRAM (под 3 ГБ)
        if torch.cuda.is_available():
            self.model.enable_model_cpu_offload()
            self.model.enable_attention_slicing()
        
        print("Model loaded successfully!")

    def generate_dsp_boom(self, duration: float = 1.0, sr: int = 16000) -> np.ndarray:
        """Генерирует процедурный низкочастотный бум через NumPy.
        
        Sine sweep + exponential decay для создания ударного эффекта.
        
        Args:
            duration: Длительность бума в секундах.
            sr: Частота дискретизации.
            
        Returns:
            NumPy массив с аудиоданными.
        """
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        # Sine sweep от низкой частоты к ещё более низкой
        f_start = 150.0
        f_end = 30.0
        # Chirp сигнал с экспоненциальным затуханием частоты
        phase = 2 * np.pi * f_end * t / (np.log(f_end / f_start) * t + 1) if f_start != f_end else 2 * np.pi * f_start * t
        carrier = np.sin(phase)
        
        # Экспоненциальное затухание амплитуды
        envelope = np.exp(-3 * t / duration)
        
        # Комбинируем
        boom = carrier * envelope
        
        # Нормализуем
        if np.max(np.abs(boom)) > 0:
            boom = boom / np.max(np.abs(boom))
        
        return boom

    def generate(self, prompt: str) -> dict:
        """Генерирует гибридный звуковой эффект (AI + DSP).
        
        Args:
            prompt: Текстовое описание желаемого звукового эффекта.
            
        Returns:
            Словарь с результатом генерации: filename, url, prompt.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # AI слой
        print(f"Generating AI layer for prompt: '{prompt}'...")
        ai_audio = self.model(
            prompt,
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        # Извлекаем AI аудио - AudioLDMPipeline возвращает dict с ключом 'audio'
        if isinstance(ai_audio, dict) and 'audio' in ai_audio:
            ai_waveform = ai_audio['audio']
        elif isinstance(ai_audio, dict) and 'waveform' in ai_audio:
            ai_waveform = ai_audio['waveform']
        elif isinstance(ai_audio, list) and len(ai_audio) > 0:
            ai_waveform = ai_audio[0]
        elif isinstance(ai_audio, np.ndarray):
            ai_waveform = ai_audio
        else:
            ai_waveform = np.array(ai_audio)
        
        # Если это 2D массив (1, samples), берем первый канал
        if isinstance(ai_waveform, np.ndarray) and ai_waveform.ndim > 1:
            ai_waveform = ai_waveform[0] if ai_waveform.shape[0] < ai_waveform.shape[1] else ai_waveform.squeeze()
        
        # AudioLDM генерирует при 16kHz, приводим к 16kHz
        target_length = 16000  # 1 секунда при 16kHz
        if len(ai_waveform) > target_length:
            ai_waveform = ai_waveform[:target_length]
        elif len(ai_waveform) < target_length:
            ai_waveform = np.pad(ai_waveform, (0, target_length - len(ai_waveform)))

        # DSP слой
        print("Generating DSP layer...")
        dsp_waveform = self.generate_dsp_boom(duration=1.0, sr=16000)

        # Микширование: AI × 0.7 + DSP × 0.5
        # Приводим к одинаковой длине
        min_len = min(len(ai_waveform), len(dsp_waveform))
        mixed = ai_waveform[:min_len] * 0.7 + dsp_waveform[:min_len] * 0.5

        # Нормализация до 0.95
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = mixed * (0.95 / max_val)

        # Генерируем уникальное имя файла
        filename = f"sfx_{uuid.uuid4().hex}.wav"
        filepath = os.path.join(self.output_dir, filename)

        # Сохраняем файл
        sf.write(filepath, mixed, 16000)
        print(f"Saved to {filepath}")

        return {
            "filename": filename,
            "url": f"/download/{filename}",
            "prompt": prompt
        }


# Глобальный экземпляр генератора
generator = SFXGenerator()