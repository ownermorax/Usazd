from time import sleep
import requests
import re
from decimal import Decimal
import os
import django
import json
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_project.settings')
django.setup()

from main.models import Profile
import datetime

from main.utils import logger

class UsdtParser:
    def __init__(self):
        self.usdt_contract = '0:b113a994b5024a16719f69139328eb759596c38a25f59028b146fecdc3621dfe'
        self.wallet_address = '0:aa88cd18b7ecd64165209f83dd795e290e9d1ceb2a9e68b2e322e250d80d2534'
        self.url = f'https://tonapi.io/v2/accounts/{self.wallet_address}/events?limit=100'
        self.seen_file = Path(__file__).parent / 'processed_transactions.json'
        self.seen = self.load_seen_transactions()

    def load_seen_transactions(self):
        if self.seen_file.exists():
            try:
                with open(self.seen_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_events', []))
            except:
                return set()
        return set()

    def save_seen_transactions(self):
        try:
            data = {'processed_events': list(self.seen)}
            with open(self.seen_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except:
            pass

    def start(self):
        while True:
            try:
                response = requests.get(self.url, timeout=30)
                response.raise_for_status()
                data = response.json()

                for event in data.get('events', []):
                    event_id = event['event_id']

                    if event_id in self.seen:
                        continue

                    for action in event['actions']:
                        if action['type'] == 'JettonTransfer':
                            transfer = action['JettonTransfer']

                            if transfer['jetton']['address'] != self.usdt_contract:
                                continue

                            if transfer['recipient']['address'] != self.wallet_address:
                                continue

                            comment = transfer.get('comment', '')
                            match = re.search(r'#id\{?(\d+)\}?', comment)

                            if match:
                                user_id = int(match.group(1))
                                decimals = transfer['jetton']['decimals']
                                amount = Decimal(transfer['amount']) / Decimal(10 ** decimals)

                                try:
                                    profile = Profile.objects.get(user_id=user_id)
                                    profile.update_balance(amount)
                                    self.seen.add(event_id)
                                    self.save_seen_transactions()
                                except Profile.DoesNotExist:
                                    logger.info(f"Профиль не найден: id{str(user_id)}")
                                except Exception as e:
                                    logger.info(f"Ошибка в парсере: {str(e)}")
                            else:
                                pass

            except Exception as e:
                logger.info(f"Ошибка в парсере: {str(e)}")
            sleep(10)

class PremiumParser:
    def __init__(self):
        pass
    def start(self):
        while True:
            try:
                for profile in Profile.objects.filter(is_vip=True):
                    if profile.vip_expire and profile.vip_expire < datetime.datetime.now():
                        profile.is_vip = False
                        profile.vip_data = ''
                        profile.save()
                        logger.info(f"VIP expired for user {profile.user.id}")
            except Exception as e:
                logger.info(f"Ошибка в парсере: {str(e)}")

            sleep(30)

class Parser:
    def __init__(self):
        pass
    def start_parser(self, mode):
        mods = {
            'usdt': UsdtParser,
            'vip': PremiumParser
        }
        sparser = mods[mode]()
        sparser.start()
        return True

parser = Parser()