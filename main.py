import csv
import json
import time

import requests
from bs4 import BeautifulSoup

# headers = {
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# }
#
# filename=input("Введите имя файла в формате 'имя файла.xml'")
#
# print('[+][+][+]СБОР ССЫЛОК[+][+][+]')
# #Сбор ссылок
# with open(filename, 'r') as file:
#     soup = BeautifulSoup(file, 'lxml')
#     urls=soup.findAll('url')
#     set_links=[]
#     for url in urls:
#         link=url.find('loc').text
#         set_links.append(link)


links_quantity = len(set_links)

print('[+][+][+]СТАРТ ПАРСИНГА[+][+][+]')


# обход ссылок
def get_parts(soup):
    """
    Собирает название запчастей
    """
    global parts
    items = soup.findAll('div', class_='item')
    for item in items:
        part_name = item.find('h3').text + ','
        parts.append(part_name)


with open(f'{filename}_Результат.csv', 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Категория', 'Бренд', 'Наименование техники', 'Продуктовый код', 'Подходящие запчасти'])
count = 0
fails_count = 0

for url in set_links:
    with open('отработанные ссылки.json', 'r', encoding='utf-8') as file:
        used_links = json.load(file)
    if url in used_links:
        print('ссылка использована ранее')
        continue
    used_links[url] = ''
    with open('отработанные ссылки.json', 'w', encoding='utf-8') as file:
        json.dump(used_links, file, indent=4, ensure_ascii=False)
    print(url)
    try:
        parts = []
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except:
            print('Время таймаута превышено')
            set_links.append(url)
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        brand = soup.find('div', class_='wrap_breadcrumbs').find('ul').findAll('li')[1].text.lower().replace('\n', '')
        title = soup.find('h1').text.lower()
        category = title.split(brand)[0].upper()
        article = title.split(brand)[1].split('(')[0].replace(' ', '').upper()
        try:
            product_code = title.split(brand)[1].split('(')[1].replace(')', '')
        except:
            product_code = '-'
        brand = brand.upper()

        try:
            pages = len(soup.find('ul', class_='pagination').findAll('li')) - 2
        except:
            pages = 1
        for page in range(1, pages + 1):
            if page == 1:
                get_parts(soup)
            else:
                try:
                    response = requests.get(f"{url}?start={page}", headers=headers, timeout=5)
                except:
                    print('Время таймаута превышено')
                    set_links.append(url)
                    continue
                soup = BeautifulSoup(response.text, 'lxml')
                get_parts(soup)

        with open(f'{filename}_Результат.csv', 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([category, brand, article, product_code, " ".join(parts)])
        count += 1
        print(print(f'[+][+][+]ОСТАЛОСЬ ОБОЙТИ {links_quantity - count} ССЫЛОК[+][+][+]'))
    except:
        with open('fail.txt', 'a', encoding='utf-8') as file:
            file.write(f'Ошибка на ссылке {url}\n')
        fails_count += 1
        print(f'Найдена ошибка номер {fails_count}')
        continue
