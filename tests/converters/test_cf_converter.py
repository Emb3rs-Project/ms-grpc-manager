from typing import Dict

from simulations.converters.cf_converter import platform_to_convert_pinch


def test_platform_to_convert_pinch(simulation_data: Dict):
    convert_pinch = platform_to_convert_pinch(initial_data=simulation_data["initialData"])
    assert isinstance(convert_pinch, dict)
    assert tuple(convert_pinch.keys()) == (
        "streams_to_analyse",
        "pinch_delta_T_min",
        "all_input_objects",
        "lifetime",
        "fuels_data",
        "number_output_options",
        "interest_rate",
    )
