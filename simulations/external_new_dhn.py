import json
import os
from re import I
import grpc
import jsonpickle

from cf.cf_models import (
    ConvertOrcOutputModel,
    ConvertSinkOutputModel,
    ConvertSourceOutputModel,
)
from cf.cf_pb2 import ConvertSourceInput, PlatformOnlyInput
from gis.gis_models import CreateNetworkOutputModel
from simulations.base_simulation import BaseSimulation
from simulations.converters.cf_converter import (
    cf_module_to_convert_source,
    platform_to_convert_sink,
    platform_to_convert_source,
    platform_to_orc_convert,
)
from simulations.converters.gis_converter import (
    cf_module_to_create_network,
    platform_to_create_network,
    teo_module_to_create_netowrk,
)

from gis.gis_pb2 import CreateNetworkInput, OptimizeNetworkInput


class ExternalNewDHN(BaseSimulation):
    def _run(self):

        ## Run CF Convert Sinks
        def run_cf_convert_sinks():
            platform = platform_to_convert_sink(initial_data=self.initial_data)

            self.request = PlatformOnlyInput(platform=json.dumps(platform))
            result = self.cf.convert_sink(self.request)
            self.river_data["convert_sink"] = result

            self.reporter.save_step_report(
                "CF Module",
                "convert_sink",
                {"platform": platform},
                ConvertSinkOutputModel().from_grpc(result).dict(),
            )

        if not self.safe_run_step("CF Module", "convert_sink", run_cf_convert_sinks):
            return

        def run_cf_convert_sources():
            # Run CF Convert Sources
            platform = platform_to_convert_source(initial_data=self.initial_data)
            cf_module = cf_module_to_convert_source(
                initial_data=self.initial_data, river_data=self.river_data
            )

            self.request = ConvertSourceInput(
                platform=json.dumps(platform),
                gis_module=json.dumps({}),
                cf_module=json.dumps(cf_module),
            )

            result = self.cf.convert_source(self.request)
            self.river_data["convert_source"] = result

            self.reporter.save_step_report(
                "CF Module",
                "convert_source",
                {"platform": platform, "cf_module": cf_module},
                ConvertSourceOutputModel().from_grpc(result).dict(),
            )

        if not self.safe_run_step(
            "CF Module", "convert_source", run_cf_convert_sources
        ):
            return

        if not self.safe_run_step(
            "CF Module", "convert_source", run_cf_convert_sources
        ):
            return

        def run_gis_create_network():
            platform = platform_to_create_network(initial_data=self.initial_data)
            cf_module = cf_module_to_create_network(river_data=self.river_data)
            teo_module = teo_module_to_create_netowrk(river_data=self.river_data)

            self.request = CreateNetworkInput(
                platform=json.dumps(platform),
                cf_module=json.dumps(cf_module),
                teo_module=json.dumps(teo_module),
            )

            result = self.gis.create_network(self.request)
            self.river_data["create_network"] = result

            self.reporter.save_step_report(
                "GIS Module",
                "create_network",
                {},
                result,
            )

        if not self.safe_run_step(
            "GIS Module", "create_network", run_gis_create_network
        ):
            return
