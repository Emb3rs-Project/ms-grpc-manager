import copy
from typing import Dict

from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel

FUELS_DATA = {
    "natural_gas": {"price": 0.02274101807185543, "co2_emissions": 0.209923664},
    "biomass": {"price": 0.043199654, "co2_emissions": 0.0108},
    "electricity": {"price": 0.089, "co2_emissions": 0.606},
    "fuel_oil": {"price": 0.047392344, "co2_emissions": 0.266272189},
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


def platform_to_convert_pinch(initial_data):
    convert_source = platform_to_convert_source(initial_data=initial_data)
    sources = convert_source["group_of_sources"]
    streams = [_build_stream(stream=stream) for source in sources for stream in source["streams"]]

    output = {
        "streams_to_analyse": [stream["id"] for stream in streams],  # noqa list - streams id to analyse
        "pinch_delta_T_min": 20,  # noqa float - Minimum delta temperature for pinch analysis [ºC]
        "all_input_objects": streams,  # noqa list - equipments (check Source/characterization/Generate_Equipment), processes (check Source/characterization/Process/process), isolated streams (check General/Simple_User/isolated_stream)
        "lifetime": None,  # int, optional - Heat exchangers lifetime. DEFAULT=20
        "fuels_data": sources[0]["fuels_data"] if len(sources) > 0 else FUELS_DATA,  # noqa dict - Fuels price and CO2 emission
        "number_output_options": None,  # int, optional - Number of solutions of each category to return. DEFAULT=3
        "interest_rate": 0.04,  # float, optional - Interest rate considered for BM
    }
    return output


def _build_stream(stream: dict) -> dict:
    stream["name"] = f"stream{stream['id']}"
    stream["fuel"] = stream.get("fuel", "none")
    stream["eff_equipment"] = stream.get("eff_equipment")
    return stream
