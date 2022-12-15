import copy
import random
import uuid
import time
import requests
import typing
import aiohttp
import asyncio
from collections import namedtuple
import datetime
import multiprocessing
import pickle

from entities import UsernameType
from entities import LiveRoomData


CB_LIVE_ROOMS_URL = "https://chaturbate.com/affiliates/api/onlinerooms/?format=json&wm=EJuLq"


async def _gather_thumbnails(
        thumbnail_url_by_username: typing.Dict[UsernameType, str]
) -> typing.Dict[UsernameType, bytes]:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:

        async def get_thumbnails_bytes(image_url):
            async with session.get(image_url) as response:
                return await response.read()

        usernames, thumbnail_urls = zip(*thumbnail_url_by_username.items())
        thumbnails_bytes = await asyncio.gather(*[get_thumbnails_bytes(url) for url in thumbnail_urls])

        return dict(zip(usernames, thumbnails_bytes))


def gather_thumbnails(
        thumbnail_url_by_username: typing.Dict[UsernameType, str],
        result: typing.Optional[dict]  # empty!
) -> typing.Dict[UsernameType, bytes]:
    result = result if result is not None else dict()
    result.update(asyncio.run(_gather_thumbnails(thumbnail_url_by_username)))
    return result


def _get_top_cb_live_rooms_raw() -> list[dict]:
    cb_live_rooms_response = requests.get(CB_LIVE_ROOMS_URL).json()

    cb_live_rooms_raw = list()
    for pos, room_item in enumerate(cb_live_rooms_response):
        if (
                pos > 100
                and room_item['num_users'] < 500
                and room_item['num_followers'] < 150_000
        ):
            continue

        room_item = copy.copy(room_item)
        room_item['position'] = pos

        cb_live_rooms_raw.append(room_item)

    return cb_live_rooms_raw


def _get_cb_live_rooms_raw(usernames: set[UsernameType]) -> list[dict]:
    cb_live_rooms_response = requests.get(CB_LIVE_ROOMS_URL).json()

    cb_live_rooms_raw = list()
    for pos, room_item in enumerate(cb_live_rooms_response):
        if room_item['username'] not in usernames:
            continue

        room_item = copy.copy(room_item)
        room_item['position'] = pos

        cb_live_rooms_raw.append(room_item)

    return cb_live_rooms_raw


def get_top_live_rooms_data():
    t1 = datetime.datetime.utcnow()
    top_cb_live_rooms_raw_1 = _get_top_cb_live_rooms_raw()
    thumbnail_url_by_username = {room_item['username']: room_item['image_url_360x270']
                                 for room_item in top_cb_live_rooms_raw_1}
    usernames = set(thumbnail_url_by_username.keys())

    manager = multiprocessing.Manager()

    thumbnail_by_username_1 = manager.dict()
    p1 = multiprocessing.Process(target=gather_thumbnails, args=(thumbnail_url_by_username, thumbnail_by_username_1))
    p1.start()

    time.sleep(100)

    t2 = datetime.datetime.utcnow()
    cb_live_rooms_raw_2 = _get_cb_live_rooms_raw(usernames)

    thumbnail_by_username_2 = manager.dict()
    p2 = multiprocessing.Process(target=gather_thumbnails, args=(thumbnail_url_by_username, thumbnail_by_username_2))
    p2.start()

    p1.join()
    p2.join()

    live_room_data_1 = list()
    live_room_data_2 = list()
    for uname in usernames:
        room_item_1 = next(i for i in top_cb_live_rooms_raw_1 if i['username'] == uname)

        live_room_data_1.append(LiveRoomData(
            uname, room_item_1['position'], thumbnail_by_username_1[uname],
            room_item_1['seconds_online'], room_item_1['num_users'], room_item_1['num_followers']
        ))

        try:  # weird..
            room_item_2 = next(i for i in cb_live_rooms_raw_2 if i['username'] == uname)
        except StopIteration:
            continue

        live_room_data_2.append(LiveRoomData(
            uname, room_item_2['position'], thumbnail_by_username_2[uname],
            room_item_2['seconds_online'], room_item_2['num_users'], room_item_2['num_followers']
        ))

    with open(f'data/{t1.isoformat()}', 'wb') as f:
        pickle.dump({t1: live_room_data_1, t2: live_room_data_2}, f)


if __name__ == '__main__':
    get_top_live_rooms_data()
    print('heh')
