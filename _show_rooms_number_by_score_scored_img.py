import copy
import random
import uuid
import time

import numpy as np
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


if __name__ == '__main__':
    for n, fname in enumerate(os.listdir('data/scored')):
        if fname.endswith('2'):
            continue

        fname.split('')
        # if n == 2:
        #     break

        with open(f'data/raw/{fname}', 'rb') as f:
            obj = pickle.load(f)

        t1, t2 = min(obj), max(obj)
        all_lrd_1, all_lrd_2 = obj[t1], obj[t2]

        all_usernames = set.intersection(*[{room_item.username for room_item in all_room_items}
                                           for all_room_items in [all_lrd_1, all_lrd_2]])

        same_pic_usernames = set()
        for uname in all_usernames:
            live_room_data_1 = next(lrd for lrd in all_lrd_1 if lrd.username == uname)
            live_room_data_2 = next(lrd for lrd in all_lrd_2 if lrd.username == uname)

            pic1 = PIL.Image.open(io.BytesIO(live_room_data_1.thumbnail_bytes))
            pic2 = PIL.Image.open(io.BytesIO(live_room_data_2.thumbnail_bytes))

            pic1_array = np.asarray(pic1)
            pic2_array = np.asarray(pic2)
            if np.all(pic1_array == pic2_array):
                same_pic_usernames.add(uname)

        filtered_obj = {k: [lrd for lrd in v if lrd.username not in same_pic_usernames] for k, v in obj.items()}

        with open(f'data/raw/{fname}', 'wb') as f:
            pickle.dump(filtered_obj, f)
