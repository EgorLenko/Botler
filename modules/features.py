import aiohttp
from aiohttp.web_exceptions import HTTPException

import asyncio

from datetime import datetime
from functools import singledispatch

from modules import bot_typing


@singledispatch
def parse_location(location, round_number: bot_typing.PositiveInt = 2):
    raise NotImplementedError(f"Unsupported type - {type(location)}")


@parse_location.register
def _(location: bot_typing.Unpackable_1D, round_number: bot_typing.PositiveInt = 2):
    lat, long, *_ = location
    return round(lat, round_number), round(long, round_number)


@parse_location.register
def _(latitude: float, longitude: float, round_number: bot_typing.PositiveInt = 2):
    lat, long = latitude, longitude
    return round(lat, round_number), round(long, round_number)


@parse_location.register
def _(location: bot_typing.DCBaseLocation | bot_typing.TGLocation, round_number: bot_typing.PositiveInt = 2):
    return round(location.latitude, round_number), round(location.longitude, round_number)


class Time:
    JSON_TIME_DATA = dict

    @staticmethod
    async def time_by_geo(latitude, longitude) -> JSON_TIME_DATA | None:

        api_url = f"https://timeapi.io/api/Time/current/coordinate?latitude={latitude}&longitude={longitude}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HTTPException()

    @staticmethod
    def get_datetime_now():
        return datetime.now()

    def get_time(self, latitude, longitude, *options) -> dict:
        json_data = asyncio.run(self.time_by_geo(latitude, longitude))
        return_dict = {}
        for option in options:
            if option == 'date-dateTime':
                return_dict['date-dateTime'] = json_data["dateTime"].split('T')[0]
            else:
                return_dict[option] = json_data[option]
        return return_dict
