import requests
import json
import datetime

class Train:
    def __init__(self):
        """Класс поезда

        Управляет составом поезда, объединяет вагоны

        :ivar carriages: Список вагонов в поезде"""
        self.carriages = [Carriage(i) for i in range(1,12)]

class Carriage:
    """Класс вагона

    Управляет составом вагона, объединяет места

    :ivar number: Номер вагона
    :ivar seats: Список мест в вагоне"""
    def __init__(self, number):
        self.number = number
        self.seats = [Seat(i) for i in range(1,101)]

class Seat:
    """Класс места

        Отвечает за отдельное место в вагоне, хранит информацию о его статусе (занято/незанято)

        :ivar number: Номер места
        :ivar is_taken: Статус места"""
    def __init__(self,number):
        self.number = number
        self.is_taken = False


class YandexAPI:
    """Класс для взаимодействия с API Яндекс.Расписания.

        Предоставляет методы для загрузки списка станций, работы с ними
        и выполнения запросов на поиск маршрутов.
    """
    def __init__(self):
        """Инициализирует экземпляр класса YandexAPI.

        Загружает конфигурацию из файла main/config.json, извлекает API-ключ
        и инициализирует пустой словарь для хранения информации о станциях.

        :raises FileNotFoundError: Если файл конфигурации не найден
        :raises KeyError: Если в конфигурации отсутствует ключ YandexAPI
        """
        with open('main/config.json') as file:
            conf = json.load(file)
            self.YandexAPI_Key = conf['keys']['YandexAPI'] #для получения ключа https://developer.tech.yandex.ru/services
        self.stations_id = {}

    def load_stations_to_json(self):
        """Загружает список станций из API Яндекс.Расписания и сохраняет в JSON-файл.

        Выполняет GET-запрос к эндпоинту stations_list API Яндекс.Расписания
        и сохраняет полученный ответ в файл main/stations.json.

        :return: None
        :rtype: None
        """
        stations_id = requests.get(f'https://api.rasp.yandex-net.ru/v3.0/stations_list/?apikey={self.YandexAPI_Key}&lang=ru_RU&format=json')
        with open('main/stations.json', 'w', encoding='utf-8') as file:
            json.dump(stations_id.json(), file, ensure_ascii=False, indent=4)

    def load_stations_to_memory(self):
        """Загружает список станций из JSON-файла в оперативную память.

        Читает файл main/stations.json, извлекает информацию о станциях
        и сохраняет соответствия между названиями станций и их кодами
        в словарь stations_id.

        :return: True в случае успешной загрузки
        :rtype: bool
        """
        with open('main/stations.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for country in data.get('countries', []):
                for region in country.get('regions', []):
                    for settlement in region.get('settlements', []):
                        for station in settlement.get('stations', []):
                            station_code = str(station.get('codes', {}).get('yandex_code'))
                            station_name = str(station.get('title'))
                            if station_code and station_name:
                                self.stations_id[station_name.lower()] = station_code
        return True

    def get_station_id(self, station_name):
        """Возвращает идентификатор станции по её названию.

            Выполняет поиск кода станции в словаре stations_id по названию станции.
            Если станция не найдена, возвращает None вместо генерации исключения.

            :param station_name: Название станции
            :type station_name: str
            :return: Код станции в системе Яндекс.Расписания или None, если станция не найдена
            :rtype: str or None
            """
        station_name = station_name.lower()
        return self.stations_id.get(station_name)

    def station_request(self, id_station_from, id_station_to, date = datetime.datetime.now().strftime('%Y-%m-%d'),lang = 'ru_RU'):
        """Выполняет поиск маршрутов между двумя станциями.

                Отправляет запрос к API Яндекс.Расписания для поиска доступных
                маршрутов между указанными станциями на заданную дату.

                :param id_station_from: Идентификатор станции отправления
                :type id_station_from: str
                :param id_station_to: Идентификатор станции назначения
                :type id_station_to: str
                :param date: Дата отправления в формате YYYY-MM-DD (по умолчанию - текущая дата)
                :type date: str
                :param lang: Язык ответа API (по умолчанию 'ru_RU')
                :type lang: str
                :return: JSON-объект с результатами поиска или сообщение об ошибке
                :rtype: dict or str
        """
        url = f'https://api.rasp.yandex-net.ru/v3.0/search/?apikey={self.YandexAPI_Key}&format=json&from={id_station_from}&to={id_station_to}&lang={lang}&page=1&date={date}&limit=500'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return f'Error: {response.status_code}\n{url}'