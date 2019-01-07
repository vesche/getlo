#!/usr/bin/env python

import sys
import click
import locast

from pick import pick

if sys.version_info[0] >= 3:
    unicode = str


def get_desc(option):
    name = option['name'].split()[0]
    title = unicode.encode(option['listings'][0]['title'], errors="ignore")
    return '{0:<8} {1}'.format(name, title.decode())


@click.command()
@click.option('--username', '-u', prompt='Username', help='Locast Username')
@click.option('--password', '-p', prompt='Password', help='Locast Password', hide_input=True)
@click.option('--vlc_location', help='Custom VLC Path', default=None)
def main(username, password, vlc_location):
    client = locast.Client(username, password, vlc_location=vlc_location)

    options = ['Boston', 'Chicago', 'Dallas', 'Denver', 'Houston', 'New York', 'Philadelphia']
    location, _ = pick(options, "Locations:", indicator='->')
    client.get_dma(location)

    stations = client.get_stations()
    station, _ = pick(stations, "Stations:", indicator='->', options_map_func=get_desc)
    client.get_station(station['id'])
    client.stream()


if __name__ == '__main__':
    main()
