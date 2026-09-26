import os
import uuid
import numpy as np
import soundfile as sf
from diffusers import AutoPipelineForText2Audio
import torch


class SFXGenerator:
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
        self.model = AutoPipelineForText2Audio.from_pretrained(
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
            num_inference_steps=20,
            audio_length_in_s=1.0,
            sample_rate=16000
        )
        
        # Извлекаем AI аудио (зависит от формата вывода diffusers)
        if isinstance(ai_audio, list) and len(ai_audio) > 0:
            ai_waveform = ai_audio[0]
        elif isinstance(ai_audio, np.ndarray):
            ai_waveform = ai_audio
        else:
            ai_waveform = np.array(ai_audio)

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