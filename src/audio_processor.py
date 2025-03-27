# audio_processor.py
import time
from typing import Literal
import wave
import sys
from vad_processor import VADProcessor

class AudioProcessor:
    def __init__(self, sample_rate=16000, channels=1, min_speach_size=10 * 1024):
        self.vad_processor = VADProcessor(sample_rate, channels)
        self.__min_speach_size = min_speach_size
    
    def monitor_audio_file(self, filename):
        """Monitor WAV file for new audio chunks"""
        with open(filename, "rb") as f:
            f.seek(44)  # Skip WAV header
            
            while True:
                chunk = f.read(self.vad_processor.CHUNK_SIZE * 2 * self.vad_processor.CHANNELS)
                if not chunk:
                    time.sleep(0.1)
                    continue
                
                result = self.vad_processor.process_audio_chunk(chunk)

                if result:
                    self.__handle_vad_result(result)
    
    def __handle_vad_result(self, result: tuple[Literal['end'], bytes] | Literal['start']):
        """Handle VAD processor output"""
        if result == "start":
            print("Speech started - handle accordingly")
            # Do something when speech starts
        
        elif isinstance(result, tuple) and result[0] == "end":
            print("Speech ended - saving audio chunk")
            self.__save_audio_chunk(result[1])
    
    def __save_audio_chunk(self, audio_data: bytes):
        """Save audio chunk to file"""
        if sys.getsizeof(audio_data) > self.__min_speach_size: 
            filename = f"speech_{int(time.time())}.wav"
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.vad_processor.SAMPLE_RATE)
                wf.writeframes(audio_data)
            print(f"Saved: {filename}")