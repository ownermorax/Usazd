# main/context_processors.py
import requests
import json
from django.conf import settings

from .forms import NeuralNetworkForm


def search_form(request):
    """
    Контекстный процессор, который:
    1. Создает форму поиска
    2. Обрабатывает поисковый запрос, если он есть
    3. Передает результаты во все шаблоны
    """

    # Создаем форму с данными из GET-запроса
    form = NeuralNetworkForm(request.GET or None)

    # Переменные для результатов
    search_query = None
    search_answer = None

    # Если форма отправлена и валидна
    if form.is_valid():
        search_query = form.cleaned_data['text']

        # Отправляем запрос к нейросети
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemma-3-12b-it",
                    "messages": [{"role": "user", "content": search_query}],
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                search_answer = result['choices'][0]['message']['content']
            else:
                search_answer = f"Ошибка API: {response.status_code}"

        except requests.exceptions.Timeout:
            search_answer = "Превышено время ожидания ответа"
        except Exception as e:
            search_answer = f"Ошибка: {str(e)}"

    # Возвращаем все данные для шаблонов
    return {
        'search_form': form,  # Форма (с сохраненным значением)
        'search_query': search_query,  # Запрос пользователя
        'search_answer': search_answer,  # Ответ нейросети
    }