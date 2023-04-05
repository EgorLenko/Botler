import json
from datetime import datetime
from functools import cached_property
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import requests

from modules.features import parse_location


class WeatherData:

    def __init__(self, latitude, longitude, date=None, img: bool = False):
        self.img: bool = img
        self.date = date
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
    def __get_meteo_data(lat, long) -> dict:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m,precipitation_probability,precipitation,weathercode&timezone=auto&forecast_days=1'

        try:
            with requests.Session() as session:
                response = session.get(url)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return {}

    def __parse_data(self, lat, long) -> dict:
        data = self.__get_meteo_data(lat, long)
        if data is None:
            return {}

        data = data['hourly']
        weather_data = zip(data['time'],
                           data['temperature_2m'],
                           data['precipitation_probability'],
                           data['precipitation'],
                           data['weathercode'])

        parsed_result_dict = {
            time.split('T')[-1]: (temp, prec_prob, prec, wmo_code)
            for time, temp, prec_prob, prec, wmo_code in weather_data
            if int(time.split('T')[-1][:2]) >= self.date.hour
        }

        return parsed_result_dict

    def daily_weather_as_pic(self):
        if not self.data:
            return self

        weather = self.data

        times = list(weather.keys())
        weather_data = np.array(list(weather.values()))

        fig, axis_1 = plt.subplots(figsize=(14, 4))

        # Create temperature plot (y - temp, x - time)
        axis_1.plot(times, weather_data[:, 0], marker='o', color='r', label='Temperature (°C)')
        axis_1.set_ylabel("Temperature (°C)")
        axis_1.set_xlabel("Time")

        # Create a secondary y-axis for precipitation probability, precipitation, and weather code
        axis_2 = axis_1.twinx()
        axis_2.plot(times, weather_data[:, 1], marker='s', color='g', label='Precipitation Probability (%)')
        axis_2.set_ylabel("Precipitation Probability (%) / Precipitation (mm)")  # / Weather Code
        axis_2.plot(times, weather_data[:, 2], marker='^', color='b', label='Precipitation (mm)')
        # axis_2.plot(times, weather_data[:, 3], marker='D', color='m', label='Weather Code')

        # Set legend for both y-axes
        lines1, labels1 = axis_1.get_legend_handles_labels()
        lines2, labels2 = axis_2.get_legend_handles_labels()
        axis_2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.title("Weather Data")

        # Create buffer for plot, save plot in buffer and return buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        return buf
