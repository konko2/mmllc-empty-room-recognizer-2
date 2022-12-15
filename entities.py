import typing
from collections import namedtuple


UsernameType = typing.NewType('UsernameType', str)

LiveRoomData = namedtuple('LiveRoomData', [
    'username',
    'position',
    'thumbnail_bytes',
    'seconds_online',
    'num_users',
    'num_followers',
])
