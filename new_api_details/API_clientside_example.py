#!/usr/bin/env python

import requests

username = ''
password = ''

r1 = requests.request(
    'POST',
    'https://api.locastnet.org/api/user/login',
    json={
        'username': username,
        'password': password
    }
)
print(r1.json())
token = r1.json()['token']

r2 = requests.request(
    'GET',
    'https://api.locastnet.org/api/user/me',
    headers={
        'authorization': 'Bearer ' + token
    }
)
print(r2.json())

zipcode = '75001'
r3 = requests.request(
    'GET',
    'https://api.locastnet.org/api/watch/dma/zip/' + zipcode,
)
print(r3.json())

ip_address = '66.97.145.100'
r4 = requests.request(
    'GET',
    'https://api.locastnet.org/api/watch/dma/ip',
    headers = {
        'client_ip': ip_address
    }
)
print(r4.json())

latitude = 32.7831
longitude = -96.8067
r5 = requests.request(
    'GET',
    'https://api.locastnet.org/api/watch/dma/{latitude}/{longitude}'.format(
        latitude=latitude,
        longitude=longitude,
    )
)
print(r5.json())

dma = '623'
r6 = requests.request(
    'GET',
    'https://api.locastnet.org/api/watch/epg/' + dma,
    headers = {
        'authorization': 'Bearer ' + token
    }
)
print(r6.json())

station_id = '1812'
r7 = requests.request(
    'GET',
    'https://api.locastnet.org/api/watch/station/{station_id}/{latitude}/{longitude}'.format(
        station_id=station_id,
        latitude=latitude,
        longitude=longitude,
    ),
    headers = {
        'authorization': 'Bearer ' + token
    }
)
print(r7.json())
