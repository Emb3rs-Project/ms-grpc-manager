import json

from cf.cf_models import ConvertOrcOutputModel, ConvertSinkOutputModel, ConvertSourceOutputModel
from cf.cf_pb2 import ConvertSourceInput, PlatformOnlyInput

from simulations.base_simulation import BaseSimulation
from simulations.converters.cf_converter import platform_to_orc_convert


class ORCSimulation(BaseSimulation):
    def _run(self) -> None:
        if not self.safe_run_step(module="CF Module", function="convert_orc", step=self.__run_cf_convert_orc):
            pass

    def __run_cf_convert_orc(self) -> None:
        platform = platform_to_orc_convert(initial_data=self.initial_data)
        convert_orc_request = PlatformOnlyInput(platform=json.dumps(platform))

        result = self.cf.convert_orc(convert_orc_request)
        self.river_data['convert_orc'] = result

        orc_output = ConvertOrcOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module='CF Module', function='convert_orc', input_data={"platform": platform}, output_data=orc_output
        )
