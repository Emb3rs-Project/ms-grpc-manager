import os
from concurrent import futures

import dotenv
import grpc
import jsonpickle

from manager.manager_pb2 import StartSimulationRequest, StartSimulationResponse
from manager.manager_pb2_grpc import ManagerServicer, add_ManagerServicer_to_server
from simulations.base_simulation import BaseSimulation
from simulations.simulation_mapper import SIMULATION_MAPPER

dotenv.load_dotenv()


class ManagerModule(ManagerServicer):
    def StartSimulation(self, request: StartSimulationRequest, context) -> StartSimulationResponse:
        simulation_metadata = jsonpickle.decode(request.simulation_metadata)
        simulation_uuid = request.simulation_uuid
        initial_data = jsonpickle.decode(request.initial_data)

        simulation_class = SIMULATION_MAPPER.get(simulation_metadata["identifier"], BaseSimulation)
        runner = simulation_class(initial_data=initial_data, simulation_session=simulation_uuid)

        try:
            runner.run()
        except Exception:
            return StartSimulationResponse(status=1)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    add_ManagerServicer_to_server(ManagerModule(), server)

    server.add_insecure_port(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")
    print(f"Manager Listening at {os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
