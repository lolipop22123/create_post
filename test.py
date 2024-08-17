# import requests

# url = 'https://h5api.m.goofish.com/h5/mtop.taobao.idlehome.home.wechat.feeds/1.0/'

# # Заголовки, необходимые для запроса
# headers = {
#     'accept': 'application/json',
#     'accept-encoding': 'gzip, deflate, br, zstd',
#     'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#     'content-type': 'application/x-www-form-urlencoded',
#     'cookie': 'mtop_partitioned_detect=1; _m_h5_tk=1b23d18a73cb2f8e07568f008427c49b_1723846451797; _m_h5_tk_enc=37be5a35e840639922844d4b178c7cd0',
#     'origin': 'https://2.taobao.com',
#     'referer': 'https://2.taobao.com/',
#     'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
#     'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
# }

# # Данные, которые будут отправлены в запросе
# data = {
#     'jsv': '2.7.2',
#     'appKey': '12574478',
#     't': '1723837906288',
#     'sign': '3b22a10282cc4e46f6b719ff71b2f569',
#     'v': '1.0',
#     'type': 'originaljson',
#     'accountSite': 'xianyu',
#     'dataType': 'json',
#     'timeout': '20000',
#     'api': 'mtop.taobao.idlehome.home.wechat.feeds',
#     'sessionOption': 'AutoLoginOnly',
#     'c': '1b23d18a73cb2f8e07568f008427c49b_1723846451797;37be5a35e840639922844d4b178c7cd0'
# }

# # Выполнение POST-запроса
# response = requests.post(url, headers=headers, data=data)

# # Вывод статуса и текста ответа
# print(response.status_code)

# try:
#     # Попытка получить JSON-ответ
#     response_json = response.json()
#     print(response_json)
# except ValueError:
#     # В случае ошибки при парсинге JSON
#     print("Ошибка при получении JSON-ответа.")


import requests


url = 'https://h5api.m.goofish.com/h5/mtop.gaia.nodejs.gaia.idle.data.gw.v2.index.get/1.0'

r = requests.get(url)

# Создаем сессию
session = requests.Session()

# Удаляем cookie 'cookie2', если он был сохранен в сессии
if 'cookie2' in session.cookies:
    del session.cookies['cookie2']

# Отправляем запрос
response = session.get(url)

# Проверяем статус ответа
if r.status_code == 200:
    # Заголовки ответа
    headers = r.headers
    
    # Извлечение интересующих параметров
    date = headers.get('Date')
    content_type = headers.get('Content-Type')
    content_length = headers.get('Content-Length')
    connection = headers.get('Connection')
    eagleeye_traceid = headers.get('EagleEye-TraceId')
    cookie = headers.get('Set-Cookie')
    
    # Вывод извлеченных параметров
    print(f"Date: {date}")
    print(f"Content-Type: {content_type}")
    print(f"Content-Length: {content_length}")
    print(f"Connection: {connection}")
    print(f"EagleEye-TraceId: {eagleeye_traceid}")
    print(f"Set-Cookie: {cookie}")
else:
    print(f"Ошибка: {r.status_code}")