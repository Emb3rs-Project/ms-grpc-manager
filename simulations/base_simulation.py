from abc import ABC, abstractmethod
from typing import Any, Dict, Callable

import grpc
from business.business_pb2_grpc import BusinessModuleStub
from cf.cf_pb2_grpc import CFModuleStub
from gis.gis_pb2_grpc import GISModuleStub
from market.market_pb2_grpc import MarketModuleStub
from teo.teo_pb2_grpc import TEOModuleStub

from config.settings import Settings
from reports.reporter import Reporter


class BaseSimulation(ABC):
    __STEP_ERROR_MESSAGES = {
        grpc.StatusCode.CANCELLED: {"message": "Request has been Cancelled"},
        grpc.StatusCode.UNAVAILABLE: {"message": "Service is not available"},
        grpc.StatusCode.UNKNOWN: {"message": "Unknown error"},
    }

    def __init__(self, initial_data: Dict[str, Any], simulation_session: str) -> None:
        self.initial_data = initial_data
        self.simulation_session = simulation_session
        self.reporter = Reporter(self.simulation_session)
        self.river_data = {}
        self.__stub_composer()

    def run(self) -> None:
        self.__simulation_started()
        self._run()
        self.__simulation_finished()

    def safe_run_step(self, module: str, function: str, step: Callable) -> bool:
        try:
            step()
        except grpc.RpcError as rpc_error:
            error_code = rpc_error.code()
            if error_message := self.__STEP_ERROR_MESSAGES.get(error_code):
                if error_code == grpc.StatusCode.UNKNOWN:
                    error_message["message"] = rpc_error.details()
                self.reporter.save_step_error(module=module, function=function, input_data={}, errors=error_message)
            return False
        except Exception as e:
            self.reporter.save_step_error(module=module, function=function, input_data={}, errors={"message": str(e)})
            return False
        return True

    def __simulation_started(self) -> None:
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION STARTED", input_data={}, output_data={}
        )

    @abstractmethod
    def _run(self) -> None:
        self.reporter.save_step_error(
            "NOT-DEFINED", "NOT-DEFINED", {}, {"message": "Simulation Metadata is Not Defined!"}
        )

    def __simulation_finished(self) -> None:
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION FINISHED", input_data={}, output_data={}
        )

    def __stub_composer(self) -> None:
        self.__cf_stub()
        self.__gis_stub()
        self.__teo_stub()
        self.__market_stub()
        self.__business_stub()

    def __cf_stub(self) -> None:
        self.cf_channel = grpc.insecure_channel(target=f"{Settings.CF_HOST}:{Settings.CF_PORT}")
        self.cf = CFModuleStub(channel=self.cf_channel)

    def __gis_stub(self) -> None:
        self.gis_channel = grpc.insecure_channel(target=f"{Settings.GIS_HOST}:{Settings.GIS_PORT}")
        self.gis = GISModuleStub(channel=self.gis_channel)

    def __teo_stub(self) -> None:
        self.teo_channel = grpc.insecure_channel(target=f"{Settings.TEO_HOST}:{Settings.TEO_PORT}")
        self.teo = TEOModuleStub(channel=self.teo_channel)

    def __market_stub(self) -> None:
        self.market_channel = grpc.insecure_channel(target=f"{Settings.MM_HOST}:{Settings.MM_PORT}")
        self.market = MarketModuleStub(channel=self.market_channel)

    def __business_stub(self) -> None:
        self.business_channel = grpc.insecure_channel(target=f"{Settings.BM_HOST}:{Settings.BM_PORT}")
        self.business = BusinessModuleStub(channel=self.business_channel)
