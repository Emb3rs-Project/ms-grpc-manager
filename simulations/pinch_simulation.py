import json

from cf.cf_models import ConvertPinchOutputModel
from cf.cf_pb2 import PlatformOnlyInput

from simulations.base_simulation import BaseSimulation
from simulations.converters.cf_converter import platform_to_convert_pinch


class PinchSimulation(BaseSimulation):
    def _run(self) -> None:
        self.safe_run_step(module="CF Module", function="convert_pinch", step=self.__run_cf_convert_pinch)

    def _run_update(self) -> None:
        raise NotImplementedError

    def __run_cf_convert_pinch(self) -> None:
        platform = platform_to_convert_pinch(initial_data=self.initial_data)
        convert_pinch_request = PlatformOnlyInput(platform=json.dumps(platform))
        pinch_input = {"platform": platform}
        self.last_request_input_data = pinch_input

        result = self.cf.convert_pinch(convert_pinch_request)
        self.river_data['convert_pinch'] = result

        pinch_output = ConvertPinchOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module='CF Module', function='convert_pinch', input_data=pinch_input, output_data=pinch_output
        )
