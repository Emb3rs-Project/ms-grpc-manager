import logging
from concurrent import futures

import grpc
import jsonpickle

from config.settings import Settings
from manager.manager_pb2 import (
    StartSimulationRequest,
    StartSimulationResponse,
    UpdateSimulationRequest,
    UpdateSimulationResponse,
)
from manager.manager_pb2_grpc import ManagerServicer, add_ManagerServicer_to_server
from simulations.base_simulation import BaseSimulation
from simulations.simulation_mapper import SIMULATION_MAPPER


class GrpcStatusCode:
    OK = 0
    CANCELLED = 1


class ManagerModule(ManagerServicer):
    def StartSimulation(self, request: StartSimulationRequest, context) -> StartSimulationResponse:
        simulation_metadata = jsonpickle.decode(request.simulation_metadata)
        simulation_uuid = request.simulation_uuid
        initial_data = jsonpickle.decode(request.initial_data)

        simulation_class = SIMULATION_MAPPER.get(simulation_metadata["identifier"], BaseSimulation)
        simulation_steps = simulation_metadata.get("steps")

        runner = simulation_class(
            simulation_session=simulation_uuid,
            simulation_steps=simulation_steps,
            initial_data=initial_data,
        )

        try:
            runner.run()
        except Exception as exc:
            logging.error(f"Exception raised running server, exc: {exc}")
            raise exc
        return StartSimulationResponse(status=GrpcStatusCode.OK)

    def UpdateSimulation(self, request: UpdateSimulationRequest, context) -> UpdateSimulationResponse:
        simulation_metadata = jsonpickle.decode(request.simulation_metadata)
        simulation_uuid = request.simulation_uuid
        data = jsonpickle.decode(request.data)

        simulation_class = SIMULATION_MAPPER.get(simulation_metadata["identifier"], BaseSimulation)
        simulation_steps = simulation_metadata.get("steps")

        runner = simulation_class(
            simulation_session=simulation_uuid,
            simulation_steps=simulation_steps,
            update_data=data,
        )

        try:
            runner.run_update()
        except Exception as exc:
            logging.error(f"Exception raised processing update request, exc: {exc}")
            raise exc
        return UpdateSimulationResponse(status=GrpcStatusCode.OK)


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=100),
        options=[
            ('grpc.max_send_message_length', Settings.GRPC_MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', Settings.GRPC_MAX_MESSAGE_LENGTH)
        ]
    )
    add_ManagerServicer_to_server(ManagerModule(), server)

    server.add_insecure_port(f"{Settings.GRPC_HOST}:{Settings.GRPC_PORT}")
    print(f"Manager Listening at {Settings.GRPC_HOST}:{Settings.GRPC_PORT}")

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
