"""Модуль для работы с нейросетью OpenRouter.

Отправляет запросы к API OpenRouter для обработки текстовых запросов.
"""
import requests
import json

from USAZD.settings import OPENROUTER_API_KEY
from main.forms import NeuralNetworkForm

OPENROUTER_API_KEY

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": OPENROUTER_API_KEY,
        "Content-Type": "application/json",
        "HTTP-Referer": "<YOUR_SITE_URL>",
        "X-OpenRouter-Title": "<YOUR_SITE_NAME>",
    },
    data=json.dumps(
        {
            "model": "google/gemma-3-12b-it",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": NeuralNetworkForm.text},
                    ],
                }
            ],
        }
    ),
)


if response.status_code == 200:
    res = response.json()
    ans = res["choices"][0]["message"]["content"]
