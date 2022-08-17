import json

from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel
from cf.cf_pb2 import ConvertSourceInput, PlatformOnlyInput
from gis.gis_pb2 import CreateNetworkInput
from teo.teo_pb2 import BuildModelInput

from simulations.base_simulation import BaseSimulation
from simulations.converters.cf_converter import (
    cf_module_to_convert_source,
    platform_to_convert_sink,
    platform_to_convert_source,
)
from simulations.converters.gis_converter import (
    cf_module_to_create_network,
    platform_to_create_network,
    teo_module_to_create_network,
)
from simulations.converters.teo_converter import (
    cf_module_to_buildmodel,
    gis_module_to_buildmodel,
    platform_to_buildmodel,
)


class ExternalNewDHN(BaseSimulation):
    def _run(self) -> None:
        if not self.safe_run_step(module="CF Module", function="convert_sink", step=self.__run_cf_convert_sinks):
            return

        if not self.safe_run_step(module="CF Module", function="convert_source", step=self.__run_cf_convert_sources):
            return

        if not self.safe_run_step(module="CF Module", function="convert_source", step=self.__run_cf_convert_sources):
            return

        if not self.safe_run_step(module="GIS Module", function="create_network", step=self.__run_gis_create_network):
            return

        if not self.safe_run_step(module="TEO Module", function="buildmodel", step=self.__run_teo_buildmodel):
            return

    def __run_cf_convert_sinks(self) -> None:
        platform = platform_to_convert_sink(initial_data=self.initial_data)
        convert_sink_request = PlatformOnlyInput(platform=json.dumps(platform))

        result = self.cf.convert_sink(convert_sink_request)
        self.river_data["convert_sink"] = result

        sink_input = {"platform": platform}
        sink_output = ConvertSinkOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module="CF Module", function="convert_sink", input_data=sink_input, output_data=sink_output
        )

    def __run_cf_convert_sources(self) -> None:
        platform = platform_to_convert_source(initial_data=self.initial_data)
        cf_module = cf_module_to_convert_source(initial_data=self.initial_data, river_data=self.river_data)
        convert_source_request = ConvertSourceInput(
            platform=json.dumps(platform),
            gis_module=json.dumps({}),
            cf_module=json.dumps(cf_module),
        )

        result = self.cf.convert_source(convert_source_request)
        self.river_data["convert_source"] = result

        source_input = {"platform": platform, "cf_module": cf_module}
        source_output = ConvertSourceOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module='CF Module', function='convert_source', input_data=source_input, output_data=source_output
        )

    def __run_gis_create_network(self):
        platform = platform_to_create_network(initial_data=self.initial_data)
        cf_module = cf_module_to_create_network(river_data=self.river_data)
        teo_module = teo_module_to_create_network(river_data=self.river_data)
        create_network_request = CreateNetworkInput(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            teo_module=json.dumps(teo_module),
        )

        result = self.gis.create_network(create_network_request)
        self.river_data["create_network"] = result

        self.reporter.save_step_report(module="GIS Module", function="create_network", input_data={}, output_data={})

    def __run_teo_buildmodel(self):
        platform = platform_to_buildmodel(initial_data=self.initial_data, river_data=self.river_data)
        cf_module = cf_module_to_buildmodel(river_data=self.river_data)
        gis_module = gis_module_to_buildmodel(river_data=self.river_data)
        build_model_request = BuildModelInput(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            gis_module=json.dumps(gis_module),
        )

        result = self.teo.buildmodel(build_model_request)
        self.river_data["buildmodel"] = result
