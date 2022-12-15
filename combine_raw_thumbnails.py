import typing
import datetime
import pickle
from entities import LiveRoomData
import os

if __name__ == '__main__':
    objs: typing.List[typing.Dict[datetime.datetime, typing.List[LiveRoomData]]]
    objs = list()

    for n, fname in enumerate(os.listdir('data/raw')):
        # if n == 2:
        #     break

        with open(f'data/raw/{fname}', 'rb') as f:
            objs.append(pickle.load(f))

    general_obj = dict()
    for obj in objs:
        general_obj |= obj

    with open('data/live_room_data.pickle', 'wb') as f:
        pickle.dump(general_obj, f)
