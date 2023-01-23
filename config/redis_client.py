import json
from enum import Enum

from redis import Redis

from config.settings import Settings
from simulations.schemas.demo_simulation import SimulationData


class RedisClient:
    def __init__(self):
        self.client: Redis = Redis(
            host=Settings.REDIS_HOST, port=Settings.REDIS_PORT, password=Settings.REDIS_PASSWORD
        )

    def get(self, simulation_session: str) -> SimulationData:
        data = self.client.get(name=simulation_session)
        if not data:
            raise RedisClientNotFoundException(f"Simulation with session {simulation_session} not exists on Redis")
        simulation_data = SimulationData(**self.__deserialize(json_data=data))
        return simulation_data

    def set(self, simulation_session: str, simulation_data: SimulationData) -> None:
        json_data = self.__serialize(data=simulation_data.dict())
        self.client.set(name=simulation_session, value=json_data)

    def delete(self, simulation_session: str) -> None:
        self.client.delete(simulation_session)

    @staticmethod
    def __serialize(data: dict) -> str:
        return json.dumps(data, default=lambda obj: obj.value if isinstance(obj, Enum) else obj)

    @staticmethod
    def __deserialize(json_data: str) -> dict:
        return json.loads(json_data)


class RedisClientNotFoundException(Exception):
    pass
