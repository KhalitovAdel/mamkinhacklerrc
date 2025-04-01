import requests
from config_provider import ConfigProvider
from rich.console import Console
from rich.markdown import Markdown

class PromptProcessor:
    __dialog_context = [
        { 
            'role': 'system', 
            'text': """
                Помоги пройти собеседование по JAVA. 
                Сейчас я буду присылать тебе вопросы, которые мне задают.
                Ответ предоставляй:
                    - Изначально короткий и тезисный блок
                    - Далее более развернуто
                
                Возможно, в каких то случаях будет требоваться очень корроткий ответ, если понадобится более разверноту, то мне зададут уточняющие вопросы.
            """
        }
    ]

    __console = Console()

    def __init__(self, config_provider: ConfigProvider):
        self.__config_provider = config_provider

    def exec(self, dialog_text: str):
        self.__dialog_context.append({ 'role': 'user', 'text': dialog_text })
        
        data = {
            "modelUri": f"gpt://{self.__config_provider.get_required_property('yandex.gpt.folder')}/yandexgpt/rc",
            "completionOptions": {
                "stream": False
            },
            "messages": self.__dialog_context,
            "json_object": False
        }

        headers = { 
            'Authorization': f"Api-Key {self.__config_provider.get_required_property('yandex.gpt.token')}",
            "Content-Type": "application/json"
        }
        
        response = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/completion', json=data, headers=headers)

        response_text = response.json()["result"]["alternatives"][0]["message"]["text"]
        self.__dialog_context.append({ 'role': 'assistant', 'text': response_text })
        
        print("_______________________ Вопрос: ")
        print(dialog_text)
        print("_______________________")

        self.__console.print(Markdown(response_text))

