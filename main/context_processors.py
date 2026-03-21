from main.forms import NeuralNetworkForm


def search_form(request):
    """Добавляет форму поиска во все шаблоны"""
    form = NeuralNetworkForm()
    return {
        'search_form': form,
    }