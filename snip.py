import requests
import json
import time

x = [
        [
            "STED.D",
            "Против"
        ],
        [
            "STED.D",
            "Хой"
        ],
        [
            "Пикчи!",
            "Я поджигаю свой дом"
        ],
        [
            "Katanacss",
            "Молодым и пьяным"
        ],
        [
            "Loqiemean",
            "ВВВ"
        ],
        [
            "МОЛОДОСТЬ ВНУТРИ",
            "Один дома"
        ]
]
alltracks = x
import_tracks = ''
url='https://music.yandex.ru/handlers/import.jsx'
for item in alltracks:
    import_tracks += ' '.join(item) + '\n'
string_of_songs=import_tracks.replace(' ','+')
json_values={
    'content':string_of_songs
}
r1_import=requests.post(url,json=json_values)
print(json.loads(r1_import.text))

# GET
id_import=json.loads(r1_import.text)['importCode']
url='https://music.yandex.ru/handlers/import.jsx'
params={
    'code':id_import
}
r2_import=requests.get(url=url, params=params)
resp = json.loads(r2_import.text)
print(resp)

while True:
    if resp['status'] == 'in-progress':
        print(resp['status'])
        time.sleep(2)
        r2_import=requests.get(url=url, params=params)
        resp = json.loads(r2_import.text)
    elif resp['status'] == 'done':
        print(resp['status'])
        trackIds = resp['trackIds']
        print(trackIds)
        break
# print(json.loads(r2_import.text))
# time.sleep(2)
# r2_import=requests.get(url=url, params=params)
# print(json.loads(r2_import.text))
# time.sleep(2)
# r2_import=requests.get(url=url, params=params)
# print(json.loads(r2_import.text))
