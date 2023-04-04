import json
from datetime import datetime
from functools import cached_property

import requests

from modules.features import parse_location


class WeatherData:

    def __init__(self, latitude, longitude, img=False):
        self.img: bool = img
        self.creation_time = datetime.now()
        self.latitude, self.longitude = parse_location(latitude, longitude, round_number=2)
        self.data: dict = self.__parse_data(self.latitude, self.longitude)

    @cached_property
    def wmo_codes(self) -> dict:
        img: bool = self.img
        file_name = "wmo_codes_img.json" if img else "wmo_codes.json"
        with open(file_name, "r") as wmo_file:
            return json.load(wmo_file)

    @staticmethod
    def __get_meteo_data(lat, long) -> dict | None:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m,precipitation_probability,precipitation,weathercode&timezone=auto&forecast_days=1'

        try:
            with requests.Session() as session:
                response = session.get(url)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def __parse_data(self, lat, long) -> dict:
        data = self.__get_meteo_data(lat, long)
        if data is None:
            return {}

        data = data['hourly']
        weather_data = zip(data['time'], data['temperature_2m'], data['precipitation_probability'],
                           data['precipitation'], data['weathercode'])
        result_dict = {time: (temp, f'{prec_prob}%', prec, wmo_code) for time, temp, prec_prob, prec, wmo_code in
                       weather_data}
        return result_dict

# def parse_data(data, *options):
#     implemented = ('open-meteo',)
#     for option in options:
#         if option == 'open-meteo':
#
#         if option not in implemented:
#             print(f'{option} not implemented currently')
#             continue
