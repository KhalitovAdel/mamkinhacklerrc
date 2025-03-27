# audio_processor.py
import time
import wave
from vad_processor import VADProcessor

class AudioProcessor:
    def __init__(self, sample_rate=16000, channels=1):
        self.vad_processor = VADProcessor(sample_rate, channels)
    
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
                self.__handle_vad_result(result)
    
    def __handle_vad_result(self, result):
        """Handle VAD processor output"""
        if not result:
            return
        
        if result == "start":
            print("Speech started - handle accordingly")
            # Do something when speech starts
        
        elif isinstance(result, tuple) and result[0] == "end":
            print("Speech ended - saving audio chunk")
            self.__save_audio_chunk(result[1])
    
    def __save_audio_chunk(self, audio_data):
        """Save audio chunk to file"""
        filename = f"speech_{int(time.time())}.wav"
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.vad_processor.SAMPLE_RATE)
            wf.writeframes(audio_data)
        print(f"Saved: {filename}")