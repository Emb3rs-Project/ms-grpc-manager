import json
import os
from re import I
import grpc
import jsonpickle
from cf.cf_models import ConvertOrcOutputModel, ConvertSinkOutputModel, ConvertSourceOutputModel
from cf.cf_pb2 import ConvertSourceInput, PlatformOnlyInput
from simulations.base_simulation import BaseSimulation
from simulations.converters.cf_converter import cf_module_to_convert_source, platform_to_convert_sink, platform_to_convert_source, platform_to_orc_convert


class ORCSimulation(BaseSimulation):

  def _run(self):
      
      def run_cf_convert_orc():
        # Run CF Convert Sources
        platform = platform_to_orc_convert(
          initial_data=self.initial_data
        )

        convert_orc_request = PlatformOnlyInput(
          platform = json.dumps(platform)
        )
        result = self.cf.convert_orc(convert_orc_request)
        self.river_data['convert_orc'] = result

        self.reporter.save_step_report(
          'CF Module', 
          'convert_orc', 
          { "platform" : platform }, 
          ConvertOrcOutputModel().from_grpc(result).dict()
        )

      if not self.safe_run_step("CF Module", "convert_orc", run_cf_convert_orc):
        pass