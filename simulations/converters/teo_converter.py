import json


def gis_module_to_buildmodel(river_data):
    optimize_network = json.loads(river_data["optimize_network"])
    return {
        "losses_in_kw": optimize_network["losses_in_kw"],
        "cost_in_kw": optimize_network["cost_in_kw"],
    }


def cf_module_to_buildmodel_sets_technologies(river_data):
    output = []
    river_convert_sink = json.loads(river_data["convert_sink"])
    river_convert_source = json.loads(river_data["convert_source"])

    output.append(river_convert_source["teo_string"])

    for sink in river_convert_sink["all_sinks_info"]["sinks"]:
        for stream in sink["streams"]:
            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["teo_equipment_name"])

    for grid in river_convert_sink["all_sinks_info"]["grid_specific"]:
        output.append(grid["teo_equipment_name"])

    for source in river_convert_source["all_sources_info"]:
        for stream in source["streams_converted"]:
            output.append(stream["teo_stream_id"])
            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["teo_equipment_name"])

    return list(filter(lambda x: (x is not None), output))


def cf_module_to_buildmodel_sets_fuels(river_data):
    output = []
    river_convert_sink = json.loads(river_data["convert_sink"])
    river_convert_source = json.loads(river_data["convert_source"])

    output.append(river_convert_source["teo_dhn"]["input_fuel"])
    output.append(river_convert_source["teo_dhn"]["output_fuel"])

    for source in river_convert_source["all_sources_info"]:
        for stream in source["streams_converted"]:
            output.append(stream["input_fuel"])
            output.append(stream["output_fuel"])

            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["input_fuel"])
                output.append(conversion_technology["output_fuel"])

    for grid in river_convert_sink["all_sinks_info"]["grid_specific"]:
        output.append(grid["input_fuel"])
        output.append(grid["output_fuel"])

    for sink in river_convert_sink["all_sinks_info"]["sinks"]:
        for stream in sink["streams"]:
            output.append(stream["demand_fuel"])
            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["input_fuel"])
                output.append(conversion_technology["output_fuel"])

    return list(dict.fromkeys(list(filter(lambda x: (x is not None), output))))


def cf_module_to_buildmodel_specified_annual_demand_cf(river_data):
    output = []
    river_convert_sink = json.loads(river_data["convert_sink"])

    for sink in river_convert_sink["all_sinks_info"]["sinks"]:
        for stream in sink["streams"]:
            output.append(
                {"fuel": stream["demand_fuel"], "value": stream["teo_yearly_demand"]}
            )

    return list(filter(lambda x: (x is not None), output))


def create_technology_cf(river_data, props):
    river_convert_source = json.loads(river_data["convert_source"])
    return river_convert_source["teo_dhn"] | props


def cf_module_to_buildmodel_technologies_cf(river_data):
    output = []
    river_convert_sink = json.loads(river_data["convert_sink"])
    river_convert_source = json.loads(river_data["convert_source"])

    output.append(create_technology_cf(river_data=river_data, props={}))

    for sink in river_convert_sink["all_sinks_info"]["sinks"]:
        for stream in sink["streams"]:
            for conversion_technology in stream["conversion_technologies"]:

                cond_input = {}
                if "input" in conversion_technology.keys():
                    cond_input["input"] = conversion_technology["input"]

                cond_technology = {}
                if "teo_equipment_name" in conversion_technology.keys():
                    cond_technology["technology"] = conversion_technology[
                        "teo_equipment_name"
                    ]

                output.append(
                    create_technology_cf(
                        river_data=river_data,
                        props={
                            "input_fuel": conversion_technology["input_fuel"],
                            "output_fuel": conversion_technology["output_fuel"],
                            "output": conversion_technology["output"],
                            "max_capacity": conversion_technology["max_capacity"],
                            "turnkey_a": conversion_technology["turnkey_a"],
                            "om_fix": conversion_technology["om_fix"],
                            "om_var": conversion_technology["om_var"],
                            "emissions_factor": conversion_technology["emissions"],
                            # "technology" : conversion_technology["technology"],
                        }
                        | cond_input
                        | cond_technology,
                    )
                )

    for grid in river_convert_sink["all_sinks_info"]["grid_specific"]:

        cond_input = {}
        if "input" in grid.keys():
            cond_input["input"] = grid["input"]

        cond_technology = {}
        if "teo_equipment_name" in grid.keys():
            cond_technology["technology"] = grid["teo_equipment_name"]

        output.append(
            create_technology_cf(
                river_data=river_data,
                props={
                    "input_fuel": grid["input_fuel"],
                    "output_fuel": grid["output_fuel"],
                    "output": grid["output"],
                    "max_capacity": grid["max_capacity"],
                    "turnkey_a": grid["turnkey_a"],
                    "om_fix": grid["om_fix"],
                    "om_var": grid["om_var"],
                    "emissions_factor": grid["emissions"],
                }
                | cond_input
                | cond_technology,
            )
        )

    for source in river_convert_source["all_sources_info"]:
        for stream in source["streams_converted"]:
            cond_input = {}
            if "input" in stream.keys():
                cond_input["input"] = stream["input"]

            cond_technology = {}
            if "teo_equipment_name" in stream.keys():
                cond_technology["technology"] = stream["teo_equipment_name"]
            elif "teo_stream_id" in stream.keys():
                cond_technology["technology"] = stream["teo_stream_id"]

            output.append(
                create_technology_cf(
                    river_data=river_data,
                    props={
                        "input_fuel": None,
                        "output_fuel": stream["output_fuel"],
                        "output": stream["output"],
                        "max_capacity": 999999999,
                        "turnkey_a": 0,
                        "om_fix": 0,
                        "om_var": 0,
                        "emissions_factor": 0,
                    }
                    | cond_input
                    | cond_technology,
                )
            )

            for conversion_technology in stream["conversion_technologies"]:

                cond_input = {}
                if "input" in conversion_technology.keys():
                    cond_input["input"] = conversion_technology["input"]

                cond_technology = {}
                if "teo_equipment_name" in conversion_technology.keys():
                    cond_technology["technology"] = conversion_technology[
                        "teo_equipment_name"
                    ]

                output.append(
                    create_technology_cf(
                        river_data=river_data,
                        props={
                            "input_fuel": conversion_technology["input_fuel"],
                            "output_fuel": conversion_technology["output_fuel"],
                            "output": conversion_technology["output"],
                            "max_capacity": conversion_technology["max_capacity"],
                            "turnkey_a": conversion_technology["turnkey_a"],
                            "om_fix": conversion_technology["om_fix"],
                            "om_var": conversion_technology["om_var"],
                            "emissions_factor": conversion_technology["emissions"],
                        }
                        | cond_input
                        | cond_technology,
                    )
                )
    for row in output:
        if row["input_fuel"] is None:
            row["input_fuel"] = ""

    return output

def cf_module_to_buildmodel_reference(river_data):
    reference = []
    river_convert_sink = json.loads(river_data["convert_sink"])
    river_convert_source = json.loads(river_data["convert_source"])

    for sink in river_convert_sink["all_sinks_info"]["sinks"]:
        for stream in sink["streams"]:
            reference.append({
                "name": stream["teo_sink_stream_id"],
                "ref_eff_equipment": stream["ref_eff_equipment"],
                "ref_fuel_emissions": stream["ref_fuel_emissions"],
                "ref_fuel_price": stream["ref_fuel_price"],
            })
                
    return list(filter(lambda x: (x is not None), reference))

def cf_module_to_buildmodel(river_data):
    river_convert_sink = json.loads(river_data["convert_sink"])
    river_convert_source = json.loads(river_data["convert_source"])

    return {
        "specified_demand_profile_cf": river_convert_sink["teo_demand_factor_group"],
        "sets_technologies": cf_module_to_buildmodel_sets_technologies(
            river_data=river_data
        ),
        "sets_fuels": cf_module_to_buildmodel_sets_fuels(river_data=river_data),
        "technologies_cf": cf_module_to_buildmodel_technologies_cf(
            river_data=river_data
        ),
        "specified_annual_demand_cf": cf_module_to_buildmodel_specified_annual_demand_cf(
            river_data=river_data
        ),
        "capacity_factor_cf": river_convert_source["teo_capacity_factor_group"],
        
        "reference": cf_module_to_buildmodel_reference(
            river_data=river_data
        ),
    }


def create_default_technology(name):
    return {
        "technology": name,
        "availability_factor": 0.95,
        "discount_rate_tech": 0.04,
        "capacity_to_activity": 8761,
        "residual_capacity": 0,
        "max_capacity_investment": 100000000000,
        "min_capacity": 0,
        "min_capacity_investment": 0,
        "annual_activity_lower_limit": 0,
        "annual_activity_upper_limit": 100000000000,
        "model_period_activity_lower_limit": 0,
        "model_period_activity_upper_limit": 1500000000000,
    }


def platform_technologies_to_buildmodel(river_data):
    return list(
        map(
            lambda x: create_default_technology(x),
            cf_module_to_buildmodel_sets_technologies(river_data=river_data),
        )
    )


def platform_to_buildmodel(initial_data, river_data):
    platform_technologies = platform_technologies_to_buildmodel(river_data=river_data)

    return {
        "platform_technologies": platform_technologies,
        "platform_sets": {
            "REGION": ["sweden"],
            "EMISSION": ["co2"],
            "TIMESLICE": [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
            ],
            "YEAR": [2022],
            "MODE_OF_OPERATION": [1, 2],
            "STORAGE": ["sto1"],
        },
        "platform_storages": [
            {
                "storage": "sto1",
                "capital_cost_storage": 10,
                "dicount_rate_sto": 0.1,
                "operational_life_sto": 100,
                "storage_max_charge": 10000,
                "storage_max_discharge": 10000,
                "l2d": 1,
                "tag_heating": 1,
                "tag_cooling": 0,
                "storage_return_temp": 50,
                "storage_supply_temp": 80,
                "storage_ambient_temp": 20,
                "residual_storage_capacity": 0,
                "max_storage_capacity": 45000,
                "storage_level_start": 10,
                "u_value": 0.14,
            }
        ],
        "platform_annual_emission_limit": [
            {"emission": "co2", "annual_emission_limit": 15000000}
        ],
        "platform_budget_limit": [{"Region": "Sweden", "budget_limit": 1}],
        "platform_technology_to_storage": [
            {
                "technology": "dhn",
                "storage": "sto1",
                "technologytostorage": 1,
                "technologyfromstorage": 1,
            }
        ],
    }
