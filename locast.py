"""locast api"""

import os
import sys
import random
import pendulum
import platform
import requests
import simplejson

from string import digits
from simplejson.errors import JSONDecodeError
from requests.exceptions import RequestException, HTTPError

BASE_URL = "https://www.locast.org"
ADMIN_URI = "/wp/wp-admin/admin-ajax.php"
LOCATIONS = {
    'Baltimore': ('39.2', '-76.6'),
    'Boston': ('42.3', '-71.1'),
    'Chicago': ('41.8', '-87.7'),
    'Dallas': ('32.7', '-96.6'),
    'Denver': ('39.7', '-105.0'),
    'Houston': ('29.7', '-95.3'),
    'Los Angeles': ('34.0', '-118.3'),
    'New York': ('40.6', '-73.9'),
    'Philadelphia': ('40.0', '-75.1'),
    'Rapid City': ('44.0', '-103.2'),
    'Sioux Falls': ('43.5', '-96.7'),
    'Washington Dc': ('38.9', '-77.0')
}
VLC_PATHS = {
    'Darwin': ['/Applications/VLC.app/Contents/MacOS/VLC'],
    'Linux': ['/usr/bin/vlc'],
    'Windows': [r'C:\Program Files\VideoLAN\VLC\vlc.exe',
                r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe']
}


class Client:
    def __init__(self, username, password, vlc_location=None):
        self.username = username
        self.latitude = None
        self.longitude = None
        self.dma = None
        self.current_stream_url = None
        self.admin_url = BASE_URL + ADMIN_URI
        self.session = requests.Session()
        self.randomize_user_agent()
        self.token = self.get_token(username, password)
        self.vlc_location = vlc_location if vlc_location else self._set_vlc()

    @staticmethod
    def _set_vlc():
        try:
            bin_paths = VLC_PATHS[platform.system()]
        except KeyError:
            print("Error! Platform not supported.")
            sys.exit(5)

        for path in bin_paths:
            if os.path.isfile(path):
                return path

    @staticmethod
    def _somewhat_randomize_location(ll):
        lat, lon = ll
        def random_13digits():
            return ''.join([random.choice(digits) for _ in range(13)])
        return (lat + random_13digits(), lon + random_13digits())

    def _locast_request(self, method, url, params=None, data=None):
        # ensure request success
        try:
            r = self.session.request(method, url, params=params, data=data)
            r.raise_for_status()
        except (RequestException, HTTPError) as e:
            print("Error!", e)
            sys.exit(1)
        # ensure json decode success
        try:
            response = r.json()
        except JSONDecodeError as e:
            print("Error!", e)
            sys.exit(2)
        return response

    def randomize_user_agent(self):
        rua = random.choice(open('useragents.txt').read().splitlines())
        self.session.headers['User-Agent'] = rua

    def set_location(self, location):
        if location.title() not in LOCATIONS.keys():
            print("Error! Try one of these locations: {locs}".format(
                locs=', '.join(LOCATIONS.keys())
            ))
            sys.exit(4)
        ll = LOCATIONS[location]
        self.latitude, self.longitude = self._somewhat_randomize_location(ll)

    def set_cookies(self):
        cookies = {
            '_member_role': '1',
            '_member_token': self.token,
            '_member_username': self.username,
            '_member_location':'{lat},{lon}'.format(
                lat=self.latitude, lon=self.longitude)
        }
        for k, v in cookies.items():
            self.session.cookies[k] = v

    def get_token(self, username, password):
        data = {
            'action': 'member_login',
            'username': username,
            'password': password
        }
        response = self._locast_request("POST", self.admin_url, data=data)
        if 'message' in response:
            print("Error!", response['message'])
            sys.exit(3)
        return response['token']

    def get_dma(self, location):
        # upon get_dma, first set location & cookies
        self.set_location(location)
        self.set_cookies()

        params = {
            "action": "get_dma",
            "lat": self.latitude,
            "lon": self.longitude
        }
        response = self._locast_request("GET", self.admin_url, params=params)
        self.dma = response['DMA']
        return self.dma

    def get_stations(self):
        params = {
            "action": "get_epgs",
            "dma": self.dma,
            "start_time": str(pendulum.now())
        }
        response = self._locast_request("GET", self.admin_url, params=params)
        return response

    def get_station(self, station_id):
        params = {
            "action": "get_station",
            "station_id": station_id,
            "lat": self.latitude,
            "lon": self.longitude
        }
        response = self._locast_request("GET", self.admin_url, params=params)
        self.current_stream_url = response['streamUrl']
        return response

    def stream(self):
        if not self.vlc_location:
            print("Error! VLC not found.")
            sys.exit(6)
        os.system('{bin_path} "{url}"'.format(
            bin_path=self.vlc_location, url=self.current_stream_url))
