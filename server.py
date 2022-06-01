import os
from concurrent import futures


import dotenv
import grpc
import jsonpickle
import json
from manager.manager_pb2 import StartSimulationRequest, StartSimulationResponse

from manager.manager_pb2_grpc import ManagerServicer, add_ManagerServicer_to_server
from simulations.base_simulation import BaseSimulation
from simulations.simulation_mapper import SIMULATION_MAPPER



dotenv.load_dotenv()


class ManagerModule(ManagerServicer):
  
  def __init__(self) -> None:
      pass

  def StartSimulation(self, request : StartSimulationRequest, context) -> StartSimulationResponse:
      simulationMetadata = jsonpickle.decode(request.simulation_metadata)
      simulationUuid = request.simulation_uuid
      initialData = jsonpickle.decode(request.initial_data)
      
      simulationClass = SIMULATION_MAPPER.get(simulationMetadata["identifier"])

      if simulationClass is None:
        simulationClass = BaseSimulation

      runner = simulationClass(
        initial_data=initialData, 
        simulation_session=simulationUuid
      )
        
      try:
        runner.run()
      except Exception:
        return StartSimulationResponse(
          status = 1
        )
        

def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
  add_ManagerServicer_to_server(ManagerModule(), server)

  server.add_insecure_port(
      f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")

  print(
      f"Manager Listening at {os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}")

  server.start()
  server.wait_for_termination()


if __name__ == '__main__':
    serve()