import json
from copy import deepcopy

from business.business_models import BMOutputModel
from business.business_pb2 import BMInput
from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel
from cf.cf_pb2 import ConvertSourceInput, PlatformOnlyInput
from gis.gis_models import CreateNetworkOutputModel, OptimizeNetworkOutputModel
from gis.gis_pb2 import CreateNetworkInput, OptimizeNetworkInput
from market.market_models import LongTermOutputModel
from market.market_pb2 import MarketInputRequest
from teo.teo_models import BuildModelOutputModel
from teo.teo_pb2 import BuildModelInput

from config.settings import Settings
from simulations.base_simulation import BaseSimulation
from simulations.converters.business_converter import (
    platform_to_financial_feasability, gis_module_to_financial_feasability, teo_module_to_financial_feasability,
    market_module_to_financial_feasability,
)
from simulations.converters.cf_converter import (
    cf_module_to_convert_source, platform_to_convert_sink, platform_to_convert_source,
)
from simulations.converters.gis_converter import (
    cf_module_to_create_network, platform_to_create_network, teo_module_to_create_network,
    cf_module_to_optimize_network, platform_to_optimize_network, teo_module_to_optimize_network,
    gis_module_to_optimize_network,
)
from simulations.converters.market_converter import (
    platform_to_long_term, cf_module_to_long_term, gis_module_to_long_term, teo_module_to_long_term,
)
from simulations.converters.teo_converter import (
    cf_module_to_buildmodel, gis_module_to_buildmodel, platform_to_buildmodel,
)


class DemoSimulation(BaseSimulation):
    _DEFAULT_STEPS = (
        "convert_sink",
        "convert_source",
        "create_network",
        "optimize_network",
        "buildmodel",
        "long_term",
        "feasability",
    )

    def _run(self) -> None:
        step_by_function_name = {
            "convert_sink": {"module": "CF Module", "function": "convert_sink", "step": self.__run_cf_convert_sink},
            "convert_source": {"module": "CF Module", "function": "convert_source", "step": self.__run_cf_convert_source},  # noqa
            "create_network": {"module": "GIS Module", "function": "create_network", "step": self.__run_gis_create_network},  # noqa
            "optimize_network": {"module": "GIS Module", "function": "optimize_network", "step": self.__run_gis_optimize_network},  # noqa
            "buildmodel": {"module": "TEO Module", "function": "buildmodel", "step": self.__run_teo_buildmodel},
            "long_term": {"module": "Market Module", "function": "long_term", "step": self.__run_market_long_term},
            "feasability": {"module": "Business Module", "function": "feasability", "step": self.__run_business_feasability},  # noqa
        }
        steps = self.simulation_steps or self._DEFAULT_STEPS
        try:
            pipeline = tuple(step_by_function_name[step_name] for step_name in steps)
        except KeyError as exc:
            raise Exception(f"Step {exc} not exist for this simulation")

        for step in pipeline:
            if not self.safe_run_step(**step):
                break

    def __run_cf_convert_sink(self) -> None:
        platform = platform_to_convert_sink(initial_data=self.initial_data)
        convert_sink_request = PlatformOnlyInput(platform=json.dumps(platform))
        sink_input = {"platform": platform}
        self.last_request_input_data = sink_input

        result = self.cf.convert_sink(convert_sink_request)
        self.river_data['convert_sink'] = result

        sink_output = ConvertSinkOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module='CF Module', function='convert_sink', input_data=sink_input, output_data=sink_output
        )

    def __run_cf_convert_source(self) -> None:
        platform = platform_to_convert_source(initial_data=self.initial_data)
        cf_module = cf_module_to_convert_source(initial_data=self.initial_data, river_data=self.river_data)
        convert_source_request = ConvertSourceInput(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            gis_module=json.dumps({}),
        )
        source_input = {"platform": platform, "cf_module": cf_module}
        self.last_request_input_data = source_input

        result = self.cf.convert_source(convert_source_request)
        self.river_data['convert_source'] = result

        source_output = ConvertSourceOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module='CF Module', function='convert_source', input_data=source_input, output_data=source_output
        )

    def __run_gis_create_network(self, iteration_mode: bool = False) -> None:
        platform = platform_to_create_network(initial_data=self.initial_data)
        cf_module = cf_module_to_create_network(river_data=self.river_data)
        teo_module = teo_module_to_create_network(river_data=self.river_data)
        create_network_request = CreateNetworkInput(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            teo_module=json.dumps(teo_module),
        )
        network_input = {"platform": platform, "cf_module": cf_module, "teo_module": teo_module}
        self.last_request_input_data = network_input

        result = self.gis.create_network(create_network_request)
        self.river_data["create_network"] = result

        if not iteration_mode:
            network_output = CreateNetworkOutputModel().from_grpc(result).dict()
            self.reporter.save_step_report(
                module="GIS Module", function="create_network", input_data=network_input, output_data=network_output
            )

    def __run_gis_optimize_network(self, iteration_mode: bool = False) -> None:
        platform = platform_to_optimize_network(initial_data=self.initial_data)
        cf_module = cf_module_to_optimize_network(river_data=self.river_data)
        teo_module = teo_module_to_optimize_network(river_data=self.river_data)
        gis_module = gis_module_to_optimize_network(initial_data=self.initial_data, river_data=self.river_data)
        optimize_network_request = OptimizeNetworkInput(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            gis_module=json.dumps(gis_module),
            teo_module=json.dumps(teo_module),
        )
        network_input = {
            "platform": platform,
            "cf_module": cf_module,
            "gis_module": gis_module,
            "teo_module": teo_module,
        }
        self.last_request_input_data = network_input

        result = self.gis.optimize_network(optimize_network_request)
        self.river_data["optimize_network"] = result

        if not iteration_mode:
            network_output = OptimizeNetworkOutputModel().from_grpc(result).dict()
            self.reporter.save_step_report(
                module="GIS Module", function="optimize_network", input_data=network_input, output_data=network_output
            )

    def __run_teo_buildmodel(self) -> None:
        if Settings.GIS_TEO_ITERATION_MODE is False:
            return self.__run_simple_teo_buildmodel()

        result = None
        buildmodel_input = None

        iterations = 0
        iteration_mode = True
        last_losses_in_kw = None
        while iteration_mode:
            if last_losses_in_kw is not None:
                iterations += 1
                self.__run_gis_create_network(iteration_mode=True)
                self.__run_gis_optimize_network(iteration_mode=True)
                losses_in_kw = gis_module_to_buildmodel(river_data=self.river_data)["losses_in_kw"]

                losses_in_kw_difference = abs(losses_in_kw - last_losses_in_kw)
                coverage_percent = losses_in_kw_difference / last_losses_in_kw * 100
                if coverage_percent < 5:
                    iteration_mode = False

            platform = platform_to_buildmodel(initial_data=self.initial_data, river_data=self.river_data)
            cf_module = cf_module_to_buildmodel(river_data=self.river_data)
            gis_module = gis_module_to_buildmodel(river_data=self.river_data)
            buildmodel_request = BuildModelInput(
                platform=json.dumps(platform),
                cf_module=json.dumps(cf_module),
                gis_module=json.dumps(gis_module),
            )
            buildmodel_input = {"platform": platform, "cf_module": cf_module, "gis_module": gis_module}
            self.last_request_input_data = buildmodel_input

            last_losses_in_kw = deepcopy(gis_module["losses_in_kw"])
            result = self.teo.buildmodel(buildmodel_request)
            self.river_data["buildmodel"] = result

        if result is None or buildmodel_input is None:
            raise Exception(f"TEO Iteration with result value = ({result}) and input value = ({buildmodel_input})")

        buildmodel_output = BuildModelOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module="TEO Module",
            function="buildmodel",
            input_data={**buildmodel_input, "iterations": iterations},
            output_data=buildmodel_output,
        )

    def __run_market_long_term(self) -> None:
        platform = platform_to_long_term(initial_data=self.initial_data)
        cf_module = cf_module_to_long_term(river_data=self.river_data)
        gis_module = gis_module_to_long_term(river_data=self.river_data)
        teo_module = teo_module_to_long_term(river_data=self.river_data)
        market_input_request = MarketInputRequest(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            gis_module=json.dumps(gis_module),
            teo_module=json.dumps(teo_module),
        )
        long_term_input = {
            "platform": platform,
            "cf_module": cf_module,
            "gis_module": gis_module,
            "teo_module": teo_module,
        }
        self.last_request_input_data = long_term_input

        result = self.market.RunLongTermMarket(market_input_request)
        self.river_data["long_term"] = result

        long_term_output = LongTermOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module="Market Module", function="long_term", input_data=long_term_input, output_data=long_term_output
        )

    def __run_business_feasability(self) -> None:
        platform = platform_to_financial_feasability(initial_data=self.initial_data)
        gis_module = gis_module_to_financial_feasability(river_data=self.river_data)
        teo_module = teo_module_to_financial_feasability(river_data=self.river_data)
        market_module = market_module_to_financial_feasability(river_data=self.river_data)
        feasability_request = BMInput(
            platform=json.dumps(platform),
            gis_modules=json.dumps(gis_module),
            teo_module=json.dumps(teo_module),
            market_module=json.dumps(market_module),
        )
        feasability_input = {
            "platform": platform,
            "gis_module": gis_module,
            "teo_module": teo_module,
            "market_module": market_module,
        }
        self.last_request_input_data = feasability_input

        result = self.business.bm(feasability_request)
        self.river_data["feasability"] = result

        feasability_output = BMOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module="Business Module",
            function="feasability",
            input_data=feasability_input,
            output_data=feasability_output,
        )

    def __run_simple_teo_buildmodel(self) -> None:
        platform = platform_to_buildmodel(initial_data=self.initial_data, river_data=self.river_data)
        cf_module = cf_module_to_buildmodel(river_data=self.river_data)
        gis_module = gis_module_to_buildmodel(river_data=self.river_data)
        buildmodel_request = BuildModelInput(
            platform=json.dumps(platform),
            cf_module=json.dumps(cf_module),
            gis_module=json.dumps(gis_module),
        )
        buildmodel_input = {"platform": platform, "cf_module": cf_module, "gis_module": gis_module}
        self.last_request_input_data = buildmodel_input

        result = self.teo.buildmodel(buildmodel_request)
        self.river_data["buildmodel"] = result

        buildmodel_output = BuildModelOutputModel().from_grpc(result).dict()
        self.reporter.save_step_report(
            module="TEO Module", function="buildmodel", input_data=buildmodel_input, output_data=buildmodel_output
        )
