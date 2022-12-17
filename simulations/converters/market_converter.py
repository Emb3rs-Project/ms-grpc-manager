import logging

from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel
from gis.gis_models import OptimizeNetworkOutputModel
from teo.teo_models import BuildModelOutputModel

from config.settings import Settings, Solver


def platform_to_short_term(initial_data):
    pass


def cf_module_to_short_term(river_data):
    pass


def gis_module_to_short_term(river_data):
    pass


def teo_module_to_short_term(river_data):
    pass


def platform_to_long_term(initial_data):
    try:
        solver_market = initial_data.get("solver_market", Settings.DEFAULT_SIMULATION_SOLVER)
        solver = Solver(solver_market)
    except (KeyError, ValueError) as exc:
        message = f"Solver chosed for Market Module is not valid: {exc}"
        logging.error(message)
        raise Exception(message)

    long_term = initial_data["input_data"]["user"]
    long_term["solver"] = solver.value
    return long_term


def cf_module_to_long_term(river_data):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])
    long_term = {
        "all_sinks_info": river_convert_sink.all_sinks_info,
        "all_sources_info": river_convert_source.all_sources_info,
    }
    return long_term


def gis_module_to_long_term(river_data):
    river_optimize_network = OptimizeNetworkOutputModel().from_grpc(river_data["optimize_network"])
    long_term = {
        "gis_data": {
            "res_sources_sinks": river_optimize_network.res_sources_sinks
        },
        "network_solution": {
            "nodes": river_optimize_network.network_solution_nodes,
            "edges": river_optimize_network.network_solution_edges,
        },
        "a_loc": {  # Maybe it is, IDK.
            f"agent_ID{index+1}": agent
            for index, agent in enumerate(river_optimize_network.selected_agents)
        }
    }
    return long_term


def teo_module_to_long_term(river_data):
    river_buildmodel = BuildModelOutputModel().from_grpc(river_data["buildmodel"])
    return river_buildmodel.dict()
