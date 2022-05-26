


from dataclasses import dataclass
import json
import os
from typing import Any, Dict
from datetime import datetime

import grpc

from cf.cf_pb2_grpc import CFModuleStub
from reports.reporter import Reporter



@dataclass
class BaseSimulation:
  initial_data: Dict[str, Any]
  simulation_session : str

  def __post_init__(self):
    self.reporter = Reporter(self.simulation_session)

    self.river_data = {}
    self.cf_channel = grpc.insecure_channel(f"{os.getenv('CF_HOST')}:{os.getenv('CF_PORT')}")
    self.cf = CFModuleStub(self.cf_channel)

  def run(self):
    self.simulation_started()
    self._run()
    self.simulation_finished()
  
  def _run(self):
    self.reporter.save_step_error("NOT-DEFINED","NOT-DEFINED",{}, {"message" : "Simulation Metadata is Not Defined!"})

  def safe_run_step(self, module, function, step):
    try:
      step()
      return True
    except grpc.RpcError as rpc_error:
      if rpc_error.code() == grpc.StatusCode.CANCELLED:
        self.reporter.save_step_error(
          module=module,
          function=function,
          input_data={},
          errors={ "message" : "Request has been Cancelled"}
        )
      elif rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
        self.reporter.save_step_error(
          module=module,
          function=function,
          input_data={},
          errors={ "message" : "Service is not available"}
        )
      return False
    except Exception as e:
      self.reporter.save_step_error(
        module=module,
        function=function,
        input_data={},
        errors={ "message" : str(e)}
      )
      return False

  def simulation_started(self):
    self.reporter.save_step_report("SIMULATOR","SIMULATION STARTED",{},{})
  
  def simulation_finished(self):
    self.reporter.save_step_report("SIMULATOR","SIMULATION FINISHED",{},{})