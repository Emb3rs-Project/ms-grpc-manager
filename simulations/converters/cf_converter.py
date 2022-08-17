import copy
from typing import Dict

from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel

FUELS_DATA = {
    "natural_gas": {"price": 0.101, "co2_emissions": 0.209923664},
    "biomass": {"price": 0.043199654, "co2_emissions": 0.0108},
    "electricity": {"price": 0.117, "co2_emissions": 0.623},
    "fuel_oil": {"price": 0.179, "co2_emissions": 0.266272189},
}


def platform_to_convert_sink(initial_data):
    group_of_sinks = []

    for sink in initial_data["sinks"]:
        _sink = copy.deepcopy(sink["values"])
        _sink["id"] = sink["id"]
        # _sink["consumer_type"] = "non-household"  # why setting to non-household???? When have the answer, remove.
        _sink["location"] = sink["location"]["data"]["center"]
        _sink["streams"] = _sink["characterization"]["streams"]
        # NEW - Where is that should locate on input_data? IDK, supposing on characterization
        _sink["fuels_data"] = _sink["characterization"].get("fuels_data", FUELS_DATA)
        # NEW
        del _sink["characterization"]
        group_of_sinks.append(_sink)

    convert_sink = {"group_of_sinks": group_of_sinks}
    return convert_sink


def platform_to_convert_source(initial_data):
    group_of_sources = []

    for source in initial_data["sources"]:
        _source = copy.deepcopy(source["values"]["properties"])
        _source["id"] = source["id"]
        _source["location"] = source["location"]["data"]["center"]
        _source["streams"] = source["values"]["characterization"]["streams"]
        # NEW - Where is that should locate on input_data? IDK, supposing on characterization
        _source["fuels_data"] = source["values"]["characterization"].get("fuels_data", FUELS_DATA)
        # NEW
        group_of_sources.append(_source)

    convert_source = {"group_of_sources": group_of_sources}
    return convert_source


def cf_module_to_convert_source(river_data: Dict, **_):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])

    output = {
        "sink_group_grid_supply_temperature": river_convert_sink.all_sinks_info["sink_group_grid_supply_temperature"],
        "sink_group_grid_return_temperature": river_convert_sink.all_sinks_info["sink_group_grid_return_temperature"]
    }

    if river_data.get("convert_source") is not None:
        river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])
        output["last_iteration_data"] = river_convert_source.dict()

    return output


def platform_to_orc_convert(initial_data):
    convert_source = platform_to_convert_source(initial_data=initial_data)
    output = convert_source["group_of_sources"][0]
    return output
