# audio_processor.py
import sys
import time
from typing import Literal

from speach_handler import SpeachHandler
from vad_processor import VADProcessor


class AudioProcessor:
    def __init__(self, speach_handler: SpeachHandler, sample_rate=16000, channels=1, min_speach_size=10 * 1024):
        self.vad_processor = VADProcessor(sample_rate, channels)
        self.__min_speach_size = min_speach_size
        self.__speach_handler = speach_handler
    
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
        if isinstance(result, tuple) and result[0] == "end":
            # print("Speech ended - saving audio chunk")
            self.__save_audio_chunk(result[1])
    
    def __save_audio_chunk(self, audio_data: bytes):
        """Save audio chunk to file"""
        if sys.getsizeof(audio_data) > self.__min_speach_size:
            self.__speach_handler.translate_to_text_process(audio_data)