import requests
import json
import datetime

class Train:
    def __init__(self):
        self.carriages = [Carriage(i) for i in range(1,12)]
class Carriage:
    def __init__(self, number):
        self.number = number
        self.seats = [Seat(i) for i in range(1,101)]

class Seat:
    def __init__(self,number):
        self.number = number
        self.is_taken = False


class YandexAPI:
    def __init__(self):
        with open('main/config.json') as file:
            conf = json.load(file)
            self.YandexAPI_Key = conf['keys']['YandexAPI'] #для получения ключа https://developer.tech.yandex.ru/services

    def load_stations_id(self):
        stations_id = requests.get(f'https://api.rasp.yandex-net.ru/v3.0/stations_list/?apikey={self.YandexAPI_Key}&lang=ru_RU&format=json')
        with open('main/stations.json', 'w', encoding='utf-8') as file:
            json.dump(stations_id.json(), file, ensure_ascii=False, indent=4)

    #def get_station_id(self, station):


    def station_request(self, id_station_from, id_station_to, date = datetime.datetime.now().strftime('%Y-%m-%d'),lang = 'ru_RU'):
        url = f'https://api.rasp.yandex-net.ru/v3.0/search/?apikey={self.YandexAPI_Key}&format=json&from={id_station_from}&to={id_station_to}&lang={lang}&page=1&date={date}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return f'Error: {response.status_code}\n{url}'

