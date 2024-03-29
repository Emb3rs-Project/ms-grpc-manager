import traceback
from abc import ABC, abstractmethod
from typing import Callable

import grpc
from business.business_pb2_grpc import BusinessModuleStub
from cf.cf_pb2_grpc import CFModuleStub
from gis.gis_pb2_grpc import GISModuleStub
from market.market_pb2_grpc import MarketModuleStub
from simulations.schemas.demo_simulation import SimulationData, IntermediateStep
from teo.teo_pb2_grpc import TEOModuleStub

from config.grpc_client import GrpcSingletonChannel
from config.redis_client import RedisClient
from config.settings import Settings
from reports.reporter import Reporter


class BaseSimulation(ABC):
    __STEP_ERROR_MESSAGES = {
        grpc.StatusCode.CANCELLED: {"message": "Request has been Cancelled"},
        grpc.StatusCode.UNAVAILABLE: {"message": "Service is not available"},
        grpc.StatusCode.UNKNOWN: {"message": "Unknown error"},
    }
    __GRPC_CHANNEL_OPTIONS = [
        ('grpc.max_send_message_length', Settings.GRPC_MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', Settings.GRPC_MAX_MESSAGE_LENGTH)
    ]
    __DEFAULT_GRPC_ERROR = {"message": "Unknown error and code"}
    __DEFAULT_SERVER_ERROR = {"message": "Internal server error"}

    def __init__(
        self,
        simulation_session: str,
        simulation_steps: list = None,
        initial_data: dict = None,
        update_data: dict = None,
    ) -> None:
        self.initial_data = initial_data
        self.update_data = update_data
        self.simulation_session = simulation_session
        self.simulation_steps = simulation_steps
        self.reporter = Reporter(session_uuid=self.simulation_session)
        self.redis = RedisClient()
        self.river_data = {}
        self.last_request_input_data = {}
        self.simulation_paused = False
        self.simulation_finished = False
        self.__stub_composer()

    def run(self) -> None:
        self.__simulation_started()
        self._run()
        if self.simulation_paused:
            return self.__simulation_paused()
        self.__simulation_finished()

    def run_update(self) -> None:
        self.__simulation_update_started()
        self._run_update()
        self.__simulation_update_finished()
        if self.simulation_paused:
            return self.__simulation_paused()
        if self.simulation_finished:
            return self.__simulation_finished()

    def safe_run_step(self, module: str, function: str, step: Callable) -> bool:
        try:
            step()
        except SimulationPausedException:
            simulation_data = SimulationData(
                intermediate_step=IntermediateStep(function),
                simulation_session=self.simulation_session,
                simulation_steps=self.simulation_steps,
                initial_data=self.initial_data,
                river_data=self.river_data,
            )
            self.redis.set(simulation_session=self.simulation_session, simulation_data=simulation_data)
            self.simulation_paused = True
            return False
        except grpc.RpcError as rpc_error:
            error_code = rpc_error.code()  # noqa
            error_message = self.__STEP_ERROR_MESSAGES.get(error_code, self.__DEFAULT_GRPC_ERROR)
            error_details = rpc_error.details()  # noqa
            error_message["detail"] = error_details
            trace_id = "Trace: "
            if trace_id in error_details:
                exception, trace, *_ = error_details.split(trace_id)
                error_message["detail"] = exception.strip()
                error_message["trace"] = trace.replace(trace_id, "")
            self.reporter.save_step_error(
                module=module, function=function, input_data=self.last_request_input_data, errors=error_message
            )
            self.simulation_finished = True
            return False
        except Exception as exc:
            error_message = self.__DEFAULT_SERVER_ERROR
            trace = traceback.format_exc()
            error_message["detail"] = str(exc) or repr(exc)
            error_message["trace"] = trace.replace(Settings.BASE_PATH, "")
            self.reporter.save_step_error(
                module=module, function=function, input_data=self.last_request_input_data, errors=error_message
            )
            self.simulation_finished = True
            return False
        return True

    def __simulation_started(self) -> None:
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION STARTED", input_data={}, output_data={}
        )

    def __simulation_update_started(self) -> None:
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION UPDATE STARTED", input_data={}, output_data={}
        )

    @abstractmethod
    def _run(self) -> None:
        self.reporter.save_step_error(
            "NOT-DEFINED", "NOT-DEFINED", {}, {"message": "Simulation Metadata is Not Defined!"}
        )

    @abstractmethod
    def _run_update(self) -> None:
        self.reporter.save_step_error(
            "NOT-IMPLEMENTED", "NOT-IMPLEMENTED", {}, {"message": "Simulation choosed does not have update method!"}
        )

    def __simulation_paused(self) -> None:
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION PAUSED", input_data={}, output_data={}
        )

    def __simulation_finished(self) -> None:
        self.redis.delete(simulation_session=self.simulation_session)
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION FINISHED", input_data={}, output_data={}
        )

    def __simulation_update_finished(self) -> None:
        self.reporter.save_step_report(
            module="SIMULATOR", function="SIMULATION UPDATE FINISHED", input_data={}, output_data={}
        )

    def __stub_composer(self) -> None:
        self.singleton_channel = GrpcSingletonChannel()
        self.__cf_stub()
        self.__gis_stub()
        self.__teo_stub()
        self.__market_stub()
        self.__business_stub()

    def __cf_stub(self) -> None:
        cf_channel = self.singleton_channel.cf
        if not Settings.GRPC_SINGLETON_CHANNEL:
            cf_channel = grpc.insecure_channel(
                target=f"{Settings.CF_HOST}:{Settings.CF_PORT}",
                options=self.__GRPC_CHANNEL_OPTIONS
            )
        self.cf = CFModuleStub(channel=cf_channel)

    def __gis_stub(self) -> None:
        gis_channel = self.singleton_channel.gis
        if not Settings.GRPC_SINGLETON_CHANNEL:
            gis_channel = grpc.insecure_channel(
                target=f"{Settings.GIS_HOST}:{Settings.GIS_PORT}",
                options=self.__GRPC_CHANNEL_OPTIONS
            )
        self.gis = GISModuleStub(channel=gis_channel)

    def __teo_stub(self) -> None:
        teo_channel = self.singleton_channel.teo
        if not Settings.GRPC_SINGLETON_CHANNEL:
            teo_channel = grpc.insecure_channel(
                target=f"{Settings.TEO_HOST}:{Settings.TEO_PORT}",
                options=self.__GRPC_CHANNEL_OPTIONS
            )
        self.teo = TEOModuleStub(channel=teo_channel)

    def __market_stub(self) -> None:
        market_channel = self.singleton_channel.market
        if not Settings.GRPC_SINGLETON_CHANNEL:
            market_channel = grpc.insecure_channel(
                target=f"{Settings.MM_HOST}:{Settings.MM_PORT}",
                options=self.__GRPC_CHANNEL_OPTIONS
            )
        self.market = MarketModuleStub(channel=market_channel)

    def __business_stub(self) -> None:
        business_channel = self.singleton_channel.business
        if not Settings.GRPC_SINGLETON_CHANNEL:
            business_channel = grpc.insecure_channel(
                target=f"{Settings.BM_HOST}:{Settings.BM_PORT}",
                options=self.__GRPC_CHANNEL_OPTIONS
            )
        self.business = BusinessModuleStub(channel=business_channel)


class SimulationPausedException(Exception):
    pass
