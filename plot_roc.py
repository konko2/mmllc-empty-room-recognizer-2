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
import os

from core import is_picture_changed
from core import score_picture_change
from entities import UsernameType
from entities import LiveRoomData
import plotly.graph_objects as go
import plotly.express as px


if __name__ == '__main__':
    empty_rooms_pics: typing.Dict[str, PIL.Image.Image] = dict()
    non_empty_rooms_pics: typing.Dict[str, PIL.Image.Image] = dict()

    for n, fname in enumerate(os.listdir('data/labeled/empty')):
        if fname.endswith('.jpg'):
            empty_rooms_pics[fname[:-4]] = PIL.Image.open(f'data/labeled/empty/{fname}')

    for n, fname in enumerate(os.listdir('data/labeled/non-empty')):
        if fname.endswith('.jpg'):
            non_empty_rooms_pics[fname[:-4]] = PIL.Image.open(f'data/labeled/non-empty/{fname}')

    empty_rooms_pics_couples: typing.List[typing.Tuple[PIL.Image.Image, PIL.Image.Image]]
    _fname_prefixes = {fname[:-2] for fname in empty_rooms_pics if fname.endswith('_1')}
    empty_rooms_pics_couples = [
        (empty_rooms_pics[prefix + '_1'], empty_rooms_pics[prefix + '_2'])
        for prefix in _fname_prefixes
    ]

    non_empty_rooms_pics_couples: typing.List[typing.Tuple[PIL.Image.Image, PIL.Image.Image]]
    _fname_prefixes = {fname[:-2] for fname in non_empty_rooms_pics if fname.endswith('_1')}
    non_empty_rooms_pics_couples = [
        (non_empty_rooms_pics[prefix + '_1'], non_empty_rooms_pics[prefix + '_2'])
        for prefix in _fname_prefixes
    ]

    l_array = list(range(30, 70))
    x = list()
    y = list()

    for l in l_array:
        empty_rooms_match = [not is_picture_changed(
            *pics,
            o=0.05,
            a=1.,
            p=1,
            b=5e-2,
            ws=(30, 30),
            st=15,
            wl=120,
            l=l
        ) for pics in empty_rooms_pics_couples]

        non_empty_rooms_match = [is_picture_changed(
            *pics,
            o=0.05,
            a=1.,
            p=1,
            b=5e-2,
            ws=(30, 30),
            st=15,
            wl=120,
            l=l
        ) for pics in non_empty_rooms_pics_couples]

        # true_positive = empty_rooms_match.count(True)
        # false_positive = non_empty_rooms_match.count(False)
        # true_negative = non_empty_rooms_match.count(True)
        # false_negative = empty_rooms_match.count(False)

        true_positive_rate = empty_rooms_match.count(True) / len(empty_rooms_pics_couples)
        false_negative_rate = empty_rooms_match.count(False) / len(empty_rooms_match)

        true_negative_rate = non_empty_rooms_match.count(True) / len(non_empty_rooms_match)
        false_positive_rate = non_empty_rooms_match.count(False) / len(non_empty_rooms_pics_couples)

        x.append(false_positive_rate)
        y.append(true_positive_rate)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=y))
    fig.add_trace(go.Scatter(x=[0., 1.], y=[0., 1.], line={'dash': 'dash', 'color': 'blue'}))
    fig.add_trace(go.Scatter(x=[0., 0., 1.], y=[0., 1., 1.], line={'dash': 'dash', 'color': 'blue'}))

    fig.update_xaxes(range=[-0.1, 1.1])
    fig.update_yaxes(range=[-0.1, 1.1])
    fig.show()

    # print('false_positive_rate: ', false_positive_rate)
    # print('false_negative_rate: ', false_negative_rate)
