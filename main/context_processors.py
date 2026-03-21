import requests
from django.conf import settings

from .forms import NeuralNetworkForm


def search_form(request):
    """
    Контекстный процессор, который:
    1. Создает форму поиска
    2. Обрабатывает поисковый запрос, если он есть
    3. Передает результаты во все шаблоны
    """

    form = NeuralNetworkForm(request.GET or None)

    search_query = None
    search_answer = None

    if form.is_valid():
        search_query = form.cleaned_data['text']

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

    return {
        'search_form': form,
        'search_query': search_query,
        'search_answer': search_answer,
    }