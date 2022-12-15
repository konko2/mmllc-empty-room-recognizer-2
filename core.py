import requests
import typing
import datetime
from PIL import Image
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
import PIL.Image
import timeit
import textwrap
import gc

from entities import UsernameType
from entities import LiveRoomData


# skimage.util.compare_images(rgb1, rgb2) -- that's just absolute difference


def get_cropped_rgb(img: Image, o: float) -> numpy.array:
    rgb = numpy.asarray(img)

    img_size = numpy.array(rgb.shape[:-1])
    offset = numpy.floor(img_size * o).astype('int')
    bbox = offset.tolist() + (img_size - offset).tolist()

    return rgb[bbox[0]:bbox[2], bbox[1]:bbox[3], :]


def get_normalized_rgbs(rgb: numpy.array) -> numpy.array:
    normalized_rgb = rgb.astype('float') / 255

    gray = skimage.color.rgb2gray(rgb)
    sobel = skimage.filters.sobel(gray)

    sobel = sobel.reshape(sobel.shape + (1, ))
    return numpy.concatenate((normalized_rgb, sobel), axis=2)


def get_pix_distance(norm_rgbs1: numpy.array, norm_rgbs2: numpy.array, p: float, a: float) -> numpy.array:
    both_norm_rgb_vals = numpy.concatenate([
        norm_rgbs1.take([0, 1, 2], 2).reshape(-1, 3),
        norm_rgbs2.take([0, 1, 2], 2).reshape(-1, 3)
    ], axis=0)
    both_norm_rgb_std = both_norm_rgb_vals.std(axis=0).clip(1e-2)
    coeff = numpy.ones(norm_rgbs1.shape) * numpy.concatenate([both_norm_rgb_std ** -p, (a, )])

    return ((norm_rgbs1 - norm_rgbs2) ** 2 * coeff).sum(axis=-1)


def convolve_pix_change(pix_change: numpy.array, ws: typing.Tuple[int, int], st: int, wl: int) -> numpy.array:
    arr = skimage.util.view_as_windows(pix_change, ws, st)
    arr = arr.reshape(arr.shape[:2] + (-1, ))
    arr = arr.sum(axis=-1)
    return arr >= wl

def is_picture_changed(img1: Image, img2: Image, *, o, a, p, b, ws, st, wl, l) -> bool:
    rgb1, rgb2 = get_cropped_rgb(img1, o), get_cropped_rgb(img2, o)
    norm_rgbs1, norm_rgbs2 = get_normalized_rgbs(rgb1), get_normalized_rgbs(rgb2)

    pix_distance = get_pix_distance(norm_rgbs1, norm_rgbs2, p, a)
    pix_change = pix_distance >= b

    conv_change = convolve_pix_change(pix_change, ws, st, wl)
    return conv_change.sum() >= l

def get_cropped_rgb_numpy(rgb: numpy.array, x_offset, y_offset) -> numpy.array:
    img_size = numpy.array(rgb.shape[:-1])
    bbox = [y_offset, x_offset, img_size[0] - y_offset, img_size[1] - x_offset]
    return rgb[bbox[0]:bbox[2], bbox[1]:bbox[3], :]

def is_picture_changed_numpy(rgb1: numpy.array, rgb2: numpy.array, *, x_offset, y_offset, a, p, b, ws, st, wl, l) -> bool:
    rgb1, rgb2 = get_cropped_rgb_numpy(rgb1, x_offset, y_offset), get_cropped_rgb_numpy(rgb2, x_offset, y_offset)
    norm_rgbs1, norm_rgbs2 = get_normalized_rgbs(rgb1), get_normalized_rgbs(rgb2)

    pix_distance = get_pix_distance(norm_rgbs1, norm_rgbs2, p, a)
    pix_change = pix_distance >= b

    conv_change = convolve_pix_change(pix_change, ws, st, wl)
    return conv_change.sum() >= l


def score_picture_change(img1: Image, img2: Image, *, o, a, p, b, ws, st, wl) -> bool:
    rgb1, rgb2 = get_cropped_rgb(img1, o), get_cropped_rgb(img2, o)
    norm_rgbs1, norm_rgbs2 = get_normalized_rgbs(rgb1), get_normalized_rgbs(rgb2)

    pix_distance = get_pix_distance(norm_rgbs1, norm_rgbs2, p, a)
    pix_change = pix_distance >= b

    conv_change = convolve_pix_change(pix_change, ws, st, wl)
    return conv_change.sum()

def _is_picture_changed_timed(img1: Image, img2: Image, *, o, a, p, b, ws, st, wl, l) -> bool:
    print()
    print("--- Beginning of is_pic_changed")
    t_beg_total = datetime.datetime.utcnow()

    t_beg = datetime.datetime.utcnow()
    rgb1, rgb2 = get_cropped_rgb(img1, o), get_cropped_rgb(img2, o)
    print('|', 'get_cropped_rgb: ', (datetime.datetime.utcnow() - t_beg).total_seconds())

    t_beg = datetime.datetime.utcnow()
    norm_rgbs1, norm_rgbs2 = get_normalized_rgbs(rgb1), get_normalized_rgbs(rgb2)
    print('|', 'get_normalized_rgbs: ', (datetime.datetime.utcnow() - t_beg).total_seconds())

    t_beg = datetime.datetime.utcnow()
    pix_distance = get_pix_distance(norm_rgbs1, norm_rgbs2, p, a)
    pix_change = pix_distance >= b
    print('|', 'get_pix_distance: ', (datetime.datetime.utcnow() - t_beg).total_seconds())

    t_beg = datetime.datetime.utcnow()
    conv_change = convolve_pix_change(pix_change, ws, st, wl)
    print('|', 'convolve_pix_change: ', (datetime.datetime.utcnow() - t_beg).total_seconds())

    print("--- end of is_pic_changed: ", (datetime.datetime.utcnow() - t_beg_total).total_seconds())

    return conv_change.sum() >= l


if __name__ == '__main__':
    obj: typing.Dict[datetime.datetime, typing.List[LiveRoomData]]
    with open('data/live_room_data.pickle', 'rb') as f:
        obj = pickle.load(f)

    thumbnail_couples: typing.List[typing.Tuple[PIL.Image.Image, PIL.Image.Image]]
    thumbnail_couples = list()

    for t1, t2 in zip(list(sorted(obj))[::2], list(sorted(obj))[1::2]):
        all_lrd_1, all_lrd_2 = obj[t1], obj[t2]

        all_usernames = set.intersection(*[{room_item.username for room_item in all_room_items}
                                           for all_room_items in [all_lrd_1, all_lrd_2]])

        for username in all_usernames:
            thumbnail_bytes_1 = next(lrd.thumbnail_bytes for lrd in all_lrd_1 if lrd.username == username)
            thumbnail_bytes_2 = next(lrd.thumbnail_bytes for lrd in all_lrd_2 if lrd.username == username)

            if thumbnail_bytes_1 == thumbnail_bytes_2:
                continue

            thumbnail_1 = PIL.Image.open(io.BytesIO(thumbnail_bytes_1))
            thumbnail_2 = PIL.Image.open(io.BytesIO(thumbnail_bytes_2))
            thumbnail_couples.append((thumbnail_1, thumbnail_2))


    o = 0.05
    a = 1.
    p = 1
    b = 5e-2
    ws = (30, 30)
    st = 15
    wl = 120
    l = 52

    # ### Timing
    # number = 100
    # t = timeit.timeit(
    #     'is_picture_changed(pic1, pic2, o=o, a=a, p=p, b=b, ws=ws, st=st, wl=wl, l=l)',
    #     setup='pic1, pic2 = random.choice(thumbnail_couples)',
    #     globals=globals(),
    #     number=number
    # )
    # print(t / number)

    pic1, pic2 = random.choice(thumbnail_couples)
    is_picture_changed(pic1, pic2, o=o, a=a, p=p, b=b, ws=ws, st=st, wl=wl, l=l)

    pic1, pic2 = skimage

    # pic1, pic2 = random.choice(thumbnail_couples)
    # _is_picture_changed_timed(pic1, pic2, o=o, a=a, p=p, b=b, ws=ws, st=st, wl=wl, l=l)
