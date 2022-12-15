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
from google.cloud import storage
import requests
import typing
import datetime
import PIL.Image
import io
import aiohttp
import asyncio
import pickle
import time
import random
import numpy
import scipy
import skimage
import skimage.color
import skimage.filters
import skimage.util
from collections import namedtuple
from pprint import pprint
import plotly
import plotly.graph_objects as go

from core import is_picture_changed
from core import score_picture_change
from entities import UsernameType
from entities import LiveRoomData

if __name__ == '__main__':
    obj: typing.Dict[datetime.datetime, typing.List[LiveRoomData]]
    with open('data/f.pickle', 'rb') as f:
        obj = pickle.load(f)

    thumbnail_couple_by_username: typing.Dict[UsernameType, typing.Tuple[PIL.Image.Image, PIL.Image.Image]]
    thumbnail_couple_by_username = dict()

    t1, t2 = min(obj), max(obj)
    all_lrd_1, all_lrd_2 = obj[t1], obj[t2]

    all_usernames = set.intersection(*[{room_item.username for room_item in all_room_items}
                                       for all_room_items in obj.values()])

    for username in all_usernames:
        thumbnail_bytes_1 = next(lrd.thumbnail_bytes for lrd in all_lrd_1 if lrd.username == username)
        thumbnail_bytes_2 = next(lrd.thumbnail_bytes for lrd in all_lrd_2 if lrd.username == username)

        if thumbnail_bytes_1 == thumbnail_bytes_2:
            continue

        thumbnail_1 = PIL.Image.open(io.BytesIO(thumbnail_bytes_1))
        thumbnail_2 = PIL.Image.open(io.BytesIO(thumbnail_bytes_2))
        thumbnail_couple_by_username[username] = (thumbnail_1, thumbnail_2)

    all_usernames = set(thumbnail_couple_by_username.keys())
    score_by_username: typing.Dict[UsernameType, int]
    score_by_username = dict()
    for username in all_usernames:
        score_by_username[username] = score_picture_change(
            *thumbnail_couple_by_username[username],
            o=0.05,
            a=1.,
            p=1,
            b=5e-2,
            ws=(30, 30),
            st=15,
            wl=120,
        )

    x = list(range(0, 301))
    y = list()

    scores = list(score_by_username.values())
    for score in x:
        y.append(scores.count(score))

    fig = go.Figure(data=[go.Bar(y=y)], layout_title_text="rooms number by score")
    fig.show()
