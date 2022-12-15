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

from entities import UsernameType
from entities import LiveRoomData

CB_LIVE_ROOMS_URL = "https://chaturbate.com/affiliates/api/onlinerooms/?format=json&wm=EJuLq"

if __name__ == '__main__':
    cli = storage.client.Client('mmllc-data-dev')
    bucket = cli.lookup_bucket('empty-rooms-thumbnails')
    for blob in bucket.list_blobs():
        if not blob.name.startswith('data/'):
            continue
        fname = blob.name.split('/')[-1]

        obj = pickle.loads(blob.download_as_bytes())
        with open(f'data/raw/{fname}', 'wb') as f:
            pickle.dump(obj, f)
