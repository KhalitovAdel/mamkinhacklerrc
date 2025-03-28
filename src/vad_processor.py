# vad_processor.py
from typing import Literal
import webrtcvad
import struct
import numpy as np
from collections import deque
from scipy import signal

class VADProcessor:
    def __init__(self, sample_rate=16000, channels=1, aggressiveness=3):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.SAMPLE_RATE = sample_rate
        self.CHANNELS = channels
        self.FRAME_DURATION = 30  # ms
        self.CHUNK_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION / 1000)
        
        # Адаптивный буфер (до 60 секунд)
        self.audio_buffer = deque(maxlen=int(60 * 1000 / self.FRAME_DURATION))
        self.is_speaking = False
        self.silence_frames = 0
        self.MIN_SILENCE_FRAMES = 25  # Увеличенный порог для шумных сред
        self.noise_level = None
        self.speech_counter = 0

    def process_audio_chunk(self, chunk) -> (tuple[Literal['end'], bytes] | Literal['start'] | None):
        """Process audio chunk with noise adaptation"""
        # Конвертация в моно
        if self.CHANNELS == 2:
            chunk = self.__convert_stereo_to_mono(chunk)
        
        # Обновление профиля шума
        self.__update_noise_profile(chunk)
        
        # Применение шумоподавления
        processed_chunk = self.__apply_noise_reduction(chunk)
        
        # Проверка VAD с адаптивным порогом
        is_speech = self.vad.is_speech(processed_chunk, self.SAMPLE_RATE)
        
        # Адаптивная логика определения речи
        if is_speech:
            self.speech_counter += 1
            self.audio_buffer.append(chunk)  # Сохраняем оригинальный chunk
            self.silence_frames = 0
            
            if not self.is_speaking and self.speech_counter > 2:
                print("🔊 Speech started!")
                self.is_speaking = True
                return "start"
        else:
            if self.is_speaking:
                self.silence_frames += 1
                
                # Динамический порог тишины в зависимости от уровня шума
                dynamic_threshold = self.MIN_SILENCE_FRAMES
                if self.noise_level and self.noise_level > 2000:  # Высокий шум
                    dynamic_threshold += 10
                
                if self.silence_frames >= dynamic_threshold:
                    print(f"🔇 Speech ended! (Noise level: {self.noise_level:.1f})")
                    self.is_speaking = False
                    self.speech_counter = 0
                    audio_data = b"".join(self.audio_buffer)
                    self.audio_buffer.clear()

                    data_size = len(audio_data)
                    header = struct.pack(
                        '<4sI4s4sIHHIIHH4sI',
                        b'RIFF',
                        36 + data_size,
                        b'WAVE',
                        b'fmt ',
                        16,  # fmt chunk size
                        1,  # audio format (PCM)
                        self.CHANNELS,
                        self.SAMPLE_RATE,
                        self.SAMPLE_RATE * self.CHANNELS * 2,  # byte rate
                        self.CHANNELS * 2,  # block align
                        16,  # bits per sample
                        b'data',
                        data_size
                    )
                    
                    return "end", header + audio_data
        
        return None

    def __apply_noise_reduction(self, chunk):
        """Простое шумоподавление"""
        samples = np.frombuffer(chunk, dtype=np.int16)
        
        # Базовое шумоподавление (фильтр высоких частот)
        b, a = signal.butter(5, 300/(self.SAMPLE_RATE/2), 'high')
        filtered = signal.filtfilt(b, a, samples)
        
        return filtered.astype(np.int16).tobytes()

    def __convert_stereo_to_mono(self, data):
        """Convert stereo to mono with noise-aware mixing"""
        samples = struct.unpack(f"<{len(data)//2}h", data)
        mono_data = bytearray()
        
        for i in range(0, len(samples), 2):
            l = samples[i]
            r = samples[i+1] if i+1 < len(samples) else l
            
            # Взвешенное смешивание с учетом уровня сигнала
            if abs(l) > abs(r):
                mono_sample = int(l * 0.7 + r * 0.3)
            else:
                mono_sample = int(l * 0.3 + r * 0.7)
                
            mono_data.extend(struct.pack("<h", mono_sample))
        
        return bytes(mono_data)

    def __update_noise_profile(self, chunk):
        """Адаптивная калибровка уровня шума"""
        samples = np.frombuffer(chunk, dtype=np.int16)
        current_level = np.mean(np.abs(samples))
        
        if self.noise_level is None:
            self.noise_level = current_level
        else:
            # Экспоненциальное скользящее среднее
            self.noise_level = 0.9 * self.noise_level + 0.1 * current_level