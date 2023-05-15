from threading import Lock

import grpc

from config.settings import Settings

_CHANNEL_OPTIONS = [
    ('grpc.max_send_message_length', Settings.GRPC_MAX_MESSAGE_LENGTH),
    ('grpc.max_receive_message_length', Settings.GRPC_MAX_MESSAGE_LENGTH)
]


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class GrpcSingletonChannel(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.cf = grpc.insecure_channel(target=f"{Settings.CF_HOST}:{Settings.CF_PORT}", options=_CHANNEL_OPTIONS)
        self.gis = grpc.insecure_channel(target=f"{Settings.GIS_HOST}:{Settings.GIS_PORT}", options=_CHANNEL_OPTIONS)
        self.teo = grpc.insecure_channel(target=f"{Settings.TEO_HOST}:{Settings.TEO_PORT}", options=_CHANNEL_OPTIONS)
        self.market = grpc.insecure_channel(target=f"{Settings.MM_HOST}:{Settings.MM_PORT}", options=_CHANNEL_OPTIONS)
        self.business = grpc.insecure_channel(target=f"{Settings.BM_HOST}:{Settings.BM_PORT}", options=_CHANNEL_OPTIONS)
