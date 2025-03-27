import subprocess
from pynput import keyboard
import time
from audio_processor import AudioProcessor

class Recorder: 
    @staticmethod
    class Record:
        def __init__(self, process):
            self.process = process
        
        def stop(self):
            return self.process.terminate()
    
    def __init__(self):
        pass
        
    def get_pulseaudio_monitor(self):
        try:
            # Получаем список источников
            result = subprocess.run(["pactl", "list", "sources", "short"], 
                                capture_output=True, text=True, check=True)
            
            # Ищем строку с .monitor
            for line in result.stdout.splitlines():
                if ".monitor" in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]  # Возвращаем имя устройства
                        
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении pactl: {e}")
        
        return None  # Если не нашли

    def record_system_audio(self):
        # Использование
        monitor_device = self.get_pulseaudio_monitor()
        if not monitor_device:
            print("Не удалось найти устройство монитора!")
            
        OUTPUT_FILE = "output.wav"
        
        # Команда для записи системного звука через PulseAudio
        cmd = [
            "parec",
            "--format=s16le",
            "--rate=16000",
            "--channels=1",
            "--device=" + monitor_device,
            "--file-format=wav",
            OUTPUT_FILE
        ]

        process = subprocess.Popen(cmd)
        
        return Recorder.Record(process)

if __name__ == "__main__":
    print("▶️  Нажмите F1 для запуска записи. Для выхода нажмите Ctrl+C")
    instance = Recorder()
    record = None
        
    def on_press(key):
        global record
        if key == keyboard.Key.f1:
            if not record:
                record = instance.record_system_audio()
                print("🛑  Нажмите F1 для остановки. Для выхода нажмите Ctrl+C")
                time.sleep(1)
                processor = AudioProcessor(sample_rate=16000, channels=1)
                processor.monitor_audio_file("output.wav")
            else:
                record.stop()
                record = None
                print("▶️  Нажмите F1 для запуска записи. Для выхода нажмите Ctrl+C")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if record:
            record.stop()
        print("Программа завершена")