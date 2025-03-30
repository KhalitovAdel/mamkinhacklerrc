import queue

from speechkit import configure_credentials, creds, model_repository
from speechkit.stt import AudioProcessingType

from config_provider import ConfigProvider
from promt_processor import PromptProcessor


class SpeachHandler:
    def __init__(self, configProvider: ConfigProvider, promptProcessor: PromptProcessor):
        self.__audio_track_queue = queue.Queue()
        self.__prompt_processor = promptProcessor
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=configProvider.get_required_property("yandex.speechkit.token")
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
            if text[0]:
                self.__prompt_processor.exec(text[0].raw_text)