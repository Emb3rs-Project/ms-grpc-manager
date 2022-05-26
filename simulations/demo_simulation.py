import json
import os
from re import I
import grpc
import jsonpickle
from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel
from cf.cf_pb2 import ConvertSourceInput, PlatformOnlyInput
from simulations.base_simulation import BaseSimulation
from simulations.converters.cf_converter import cf_module_to_convert_source, platform_to_convert_sink, platform_to_convert_source


class DemoSimulation(BaseSimulation):

  def _run(self):

      ## Run CF Convert Sinks
      def run_cf_convert_sinks():
        platform = platform_to_convert_sink(
          initial_data=self.initial_data
        )

        convert_sink_request = PlatformOnlyInput(
          platform = json.dumps(platform)
        )
        result = self.cf.convert_sink(convert_sink_request)
        self.river_data['convert_sink'] = result

        self.reporter.save_step_report(
          'CF Module', 
          'convert_sink', 
          { "platform" : platform }, 
          ConvertSinkOutputModel().from_grpc(result).dict()
        )

      if not self.safe_run_step("CF Module", "convert_sink", run_cf_convert_sinks):
        pass
      
      def run_cf_convert_sources():
        # Run CF Convert Sources
        platform = platform_to_convert_source(
          initial_data=self.initial_data
        )
        cf_module = cf_module_to_convert_source(
          initial_data=self.initial_data,
          river_data=self.river_data
        )

        convert_source_request = ConvertSourceInput(
          platform = json.dumps(platform),
          gis_module = json.dumps({}),
          cf_module = json.dumps(cf_module)
        )

        result = self.cf.convert_source(convert_source_request)
        self.river_data['convert_source'] = result

        self.reporter.save_step_report(
          'CF Module', 
          'convert_source', 
          { 
            "platform" : platform ,
            "cf_module" : cf_module
          }, 
          ConvertSourceOutputModel().from_grpc(result).dict()
        )

      if not self.safe_run_step("CF Module", "convert_source", run_cf_convert_sources):
        pass
      
      if not self.safe_run_step("CF Module", "convert_source", run_cf_convert_sources):
        pass