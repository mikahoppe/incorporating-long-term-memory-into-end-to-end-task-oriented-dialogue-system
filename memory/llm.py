import os
import threading
from enum import Enum

import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam


class Provider(Enum):
    OPENAI = ""
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure"
    AZURE_MISTRAL = "mistral"


def call(result, parameters):
    response = openai.chat.completions.create(messages=parameters["messages"], model=parameters["model"])
    result[0] = response


def chat_threaded(parameters):
    timeout = parameters.pop("timeout", None)

    result = [None]

    api_thread = threading.Thread(target=call, args=(result, parameters))
    api_thread.start()
    api_thread.join(timeout=timeout)

    # Set the timeout for the API call
    if api_thread.is_alive():
        api_thread.join(timeout=timeout + 1)
        return {
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "API Timeout"
                    },
                    "finish_reason": "timeout"
                }
            ]
        }

    return result[0]


class Client:
    def __init__(self, provider: Provider, model_name: str) -> None:
        self.model = (
            f"{provider.value}/{model_name}" if provider.value else model_name
        )

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def client(self):
        return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="http://0.0.0.0:4000")

    def complete(
        self, messages: list[ChatCompletionMessageParam], stream: bool = False
    ) -> str:
        try:
            response = chat_threaded({
                "model": "gpt-4-turbo",
                "messages": messages
            })

            return response.choices[0].message.content
        except Exception as e:
            pass
