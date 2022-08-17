import logging
from concurrent import futures

import grpc
import jsonpickle

from config.settings import Settings
from manager.manager_pb2 import StartSimulationRequest, StartSimulationResponse
from manager.manager_pb2_grpc import ManagerServicer, add_ManagerServicer_to_server
from simulations.base_simulation import BaseSimulation
from simulations.simulation_mapper import SIMULATION_MAPPER

GRPC_STATUS_CODE_OK = 0
GRPC_STATUS_CODE_CANCELLED = 1


class ManagerModule(ManagerServicer):
    def StartSimulation(self, request: StartSimulationRequest, context) -> StartSimulationResponse:
        simulation_metadata = jsonpickle.decode(request.simulation_metadata)
        simulation_uuid = request.simulation_uuid
        initial_data = jsonpickle.decode(request.initial_data)

        simulation_class = SIMULATION_MAPPER.get(simulation_metadata["identifier"], BaseSimulation)
        runner = simulation_class(initial_data=initial_data, simulation_session=simulation_uuid)

        try:
            runner.run()
        except Exception as exc:
            logging.error(f"Exception was raised running server, exc: {exc}")
            return StartSimulationResponse(status=GRPC_STATUS_CODE_CANCELLED)
        return StartSimulationResponse(status=GRPC_STATUS_CODE_OK)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    add_ManagerServicer_to_server(ManagerModule(), server)

    server.add_insecure_port(f"{Settings.GRPC_HOST}:{Settings.GRPC_PORT}")
    print(f"Manager Listening at {Settings.GRPC_HOST}:{Settings.GRPC_PORT}")

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
