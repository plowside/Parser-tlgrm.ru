import shutil
import time
from typing import Tuple

import async_tls_client
import asyncio
import os
import re
import sys
from loguru import logger

from config import *


def color_formatter(record):
    message = record["message"].replace("{", "{{").replace("}", "}}")
    state = record["extra"].get("state", None)

    if re.search(r'\[\+\]', message):
        message = message.replace('[+]', f'<green>[{state+"|" if state else ""}+]</green>')
    elif re.search(r'\[\-\]', message):
        message = message.replace('[-]', f'<red>[{state+"|" if state else ""}-]</red>')
    elif re.search(r'\[\!\]', message):
        message = message.replace('[!]', f'<yellow>[{state+"|" if state else ""}!]</yellow>')
    elif re.search(r'\[\*\]', message):
        message = message.replace('[*]', f'<cyan>[{state+"|" if state else ""}*]</cyan>')
    elif re.search(r'\[\+\+\]', message):
        message = message.replace('[++]', f'<cyan>[{state+"|" if state else ""}+]</cyan>')

    return f"{message}\n"

logger.remove()

logger.add(
    sys.stdout,
    format=color_formatter,
    level="INFO",
    colorize=True
)

logger.add(
    "requests.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
    level="DEBUG",
    encoding="utf-8",
    rotation="50 MB",
    retention="7 days",
)




class nigga_pars:
    def __init__(self):
        self.ses = async_tls_client.AsyncSession(random_tls_extension_order=True)
        self.get_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }

    async def get_categories(self):
        req = await self.ses.get('https://tlgrm.ru/channels', headers=self.get_headers)
        logger.debug(f'response to tlgrm.ru/channels: status={req.status_code}')
        result = req.text
        categories = re.findall(r'channel-category--([^\s{}"]+)', result)
        logger.info(f'[+] Parsed categories: {len(categories)}')
        return list(set(categories))



    async def get_channels_by_category(self, category):
        req = await self.ses.get(f'https://tlgrm.ru/channels/{category}', params={'page': '1'}, headers={**self.get_headers, 'x-requested-with': 'XMLHttpRequest'})
        logger.debug(f'response to tlgrm.ru/channels/{category}?page=1: status={req.status_code}')
        resp_json = req.json()
        logger.info(f'[+] Info about [{category}]: pages={resp_json.get("last_page", "UNKNOWN")} | channels_total={resp_json.get("total", "UNKNOWN")}')

        tasks = []
        for page in range(1, resp_json.get("last_page", 1) + 1):
            tasks.append(asyncio.create_task(self.get_channel_by_category(category, page)))

        results = await asyncio.gather(*tasks)
        results_sorted = sorted(results, key=lambda x: x[1])

        results = []
        for list_objs in results_sorted:
            for dict_list_objs in list_objs:
                if not isinstance(dict_list_objs, list):
                    continue
                for dict_objs in dict_list_objs:
                    results.append(f"{('t.me/' if 't.me/' not in dict_objs['link'] else '')+dict_objs['link']};{category}")

        return results, category

    async def get_channel_by_category(self, category: str, page: int) -> Tuple[list, int]:
        req = await self.ses.get(f'https://tlgrm.ru/channels/{category}', params={'page': str(page)}, headers={**self.get_headers, 'x-requested-with': 'XMLHttpRequest'})
        logger.debug(f'response to tlgrm.ru/channels/{category}?page={page}: status={req.status_code}')
        resp_json = req.json()
        return resp_json['data'], page




    async def run_parsing(self):
        start_ts = time.time()
        categories = await self.get_categories()

        tasks = []
        for category in categories:
            tasks.append(asyncio.create_task(self.get_channels_by_category(category)))

        results = await asyncio.gather(*tasks)
        parsed_categories = []
        parsed_channels_count = 0

        if SAVE_FORMATS['rewrite']:
            open(SAVE_FORMATS['all_in_one_filename'], 'w', encoding='utf-8').close()
            if os.path.exists(SAVE_FORMATS['each_file_by_category_directory']):
                shutil.rmtree(SAVE_FORMATS['each_file_by_category_directory'])

        for parsed_channels, category in results:
            parsed_categories.append(category)
            parsed_channels_count += len(parsed_channels)
            if SAVE_FORMATS['all_in_one']:
                open(SAVE_FORMATS['all_in_one_filename'], 'a', encoding='utf-8').write('\n'.join(parsed_channels) + '\n')

            if SAVE_FORMATS['each_file_by_category']:
                os.makedirs(SAVE_FORMATS['each_file_by_category_directory'], exist_ok=True)
                open(f"{SAVE_FORMATS['each_file_by_category_directory']}/{SAVE_FORMATS['each_file_by_category_filename'].format(category=category)}", 'a', encoding='utf-8').write('\n'.join(parsed_channels) + '\n')

        logger.info(f'''\n\n\n\n[+] Parsing finished\n[+] Total time: {(time.time() - start_ts):.2f} seconds\n    Parsed categories: {len(parsed_categories)}\n    Parsed channels: {parsed_channels_count}\n\n[!] Respect to LUCKYBANANA5894''')

if __name__ == "__main__":
    if not BY_LUCKYBANANA5894:
        logger.warning("[!] LUCKYBANANA5894 switch is off. This script is not responsible for any damages caused by its use (т.е. ты ниггер).")
    z = nigga_pars()
    v = asyncio.run(z.run_parsing())