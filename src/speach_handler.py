import queue

from speechkit import configure_credentials, creds, model_repository
from speechkit.stt import AudioProcessingType

from config_provider import ConfigProvider


class SpeachHandler:
    def __init__(self, configProvider: ConfigProvider):
        self.__audio_track_queue = queue.Queue()
        token = configProvider.get_required_property("yandex.speechkit.token")
        
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=token
            )
        )

        self.__model = model_repository.recognition_model()
        self.__model.model = 'general'
        self.__model.language = 'ru-RU'
        self.__model.audio_processing_type = AudioProcessingType.Full

    def translate_to_text_process(self, audio_track: bytes):
        self.__audio_track_queue.put(audio_track)
        self.__process()
      
    def __process(self):
        while not self.__audio_track_queue.empty():
            audio_track = self.__audio_track_queue.get()
            text = self.__model.transcribe(audio=audio_track)
            print(text)