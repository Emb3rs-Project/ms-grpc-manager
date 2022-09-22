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
    input_data = initial_data["input_data"]

    output = convert_source["group_of_sources"][0]
    output["get_best_number"] = input_data["get_best_number"]
    output["orc_years_working"] = input_data["orc_years_working"]
    output["orc_T_evap"] = input_data["orc_T_evap"]
    output["orc_T_cond"] = input_data["orc_T_cond"]

    return output


def platform_to_convert_pinch(initial_data):
    pinch_analysis_data = initial_data["input_data"]["pinch_analysis"]
    convert_source = platform_to_convert_source(initial_data=initial_data)
    sources = convert_source["group_of_sources"]
    streams = [_build_stream(stream=stream) for source in sources for stream in source["streams"]]

    output = {
        "streams_to_analyse": [stream["id"] for stream in streams],
        "pinch_delta_T_min": pinch_analysis_data["pinch_delta_T_min"],
        "all_input_objects": streams,
        "lifetime": pinch_analysis_data["lifetime"],
        "fuels_data": sources[0]["fuels_data"] if len(sources) > 0 else FUELS_DATA,
        "number_output_options": pinch_analysis_data["number_output_options"],
        "interest_rate": pinch_analysis_data["interest_rate"],
    }
    return output


def _build_stream(stream: dict) -> dict:
    stream["name"] = f"stream{stream['id']}"
    stream["fuel"] = stream.get("fuel", "none")
    stream["eff_equipment"] = stream.get("eff_equipment")
    return stream
