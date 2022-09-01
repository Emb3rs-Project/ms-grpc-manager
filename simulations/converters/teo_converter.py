from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel
from gis.gis_models import OptimizeNetworkOutputModel


def gis_module_to_buildmodel(river_data):
    river_optimize_network = OptimizeNetworkOutputModel().from_grpc(river_data["optimize_network"])
    buildmodel = {
        "losses_in_kw": river_optimize_network.losses_cost_kw["losses_in_kw"],
        "cost_in_kw": river_optimize_network.losses_cost_kw["cost_in_kw"],
    }
    return buildmodel


def cf_module_to_buildmodel_sets_technologies(river_data):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])

    output = [river_convert_source.teo_string]

    for sink in river_convert_sink.all_sinks_info["sinks"]:
        for stream in sink["streams"]:
            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["teo_equipment_name"])

    for grid in river_convert_sink.all_sinks_info["grid_specific"]:
        output.append(grid["teo_equipment_name"])

    for source in river_convert_source.all_sources_info:
        for stream in source["streams_converted"]:
            output.append(stream["teo_stream_id"])
            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["teo_equipment_name"])

    return list(filter(lambda x: (x is not None), output))


def cf_module_to_buildmodel_sets_fuels(river_data):
    output = []
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])

    output.append(river_convert_source.teo_dhn["input_fuel"])
    output.append(river_convert_source.teo_dhn["output_fuel"])

    for source in river_convert_source.all_sources_info:
        for stream in source["streams_converted"]:
            output.append(stream["input_fuel"])
            output.append(stream["output_fuel"])

            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["input_fuel"])
                output.append(conversion_technology["output_fuel"])

    for grid in river_convert_sink.all_sinks_info["grid_specific"]:
        output.append(grid["input_fuel"])
        output.append(grid["output_fuel"])

    for sink in river_convert_sink.all_sinks_info["sinks"]:
        for stream in sink["streams"]:
            output.append(stream["demand_fuel"])
            for conversion_technology in stream["conversion_technologies"]:
                output.append(conversion_technology["input_fuel"])
                output.append(conversion_technology["output_fuel"])

    return list(dict.fromkeys(list(filter(lambda x: (x is not None), output))))


def cf_module_to_buildmodel_specified_annual_demand_cf(river_data):
    output = []
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])

    for sink in river_convert_sink.all_sinks_info["sinks"]:
        for stream in sink["streams"]:
            output.append({"fuel": stream["demand_fuel"], "value": stream["teo_yearly_demand"]})

    return list(filter(lambda x: (x is not None), output))


def create_technology_cf(river_data, props):
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])
    return river_convert_source.teo_dhn | props


def cf_module_to_buildmodel_technologies_cf(river_data):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])

    output = [create_technology_cf(river_data=river_data, props={})]

    for sink in river_convert_sink.all_sinks_info["sinks"]:
        for stream in sink["streams"]:
            for conversion_technology in stream["conversion_technologies"]:

                cond_input = {}
                if "input" in conversion_technology.keys():
                    cond_input["input"] = conversion_technology["input"]

                cond_technology = {}
                if "teo_equipment_name" in conversion_technology.keys():
                    cond_technology["technology"] = conversion_technology["teo_equipment_name"]

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
                        } | cond_input | cond_technology,
                    )
                )

    for grid in river_convert_sink.all_sinks_info["grid_specific"]:

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
                } | cond_input | cond_technology,
            )
        )

    for source in river_convert_source.all_sources_info:
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
                    } | cond_input | cond_technology,
                )
            )

            for conversion_technology in stream["conversion_technologies"]:

                cond_input = {}
                if "input" in conversion_technology.keys():
                    cond_input["input"] = conversion_technology["input"]

                cond_technology = {}
                if "teo_equipment_name" in conversion_technology.keys():
                    cond_technology["technology"] = conversion_technology["teo_equipment_name"]

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
                        } | cond_input | cond_technology,
                    )
                )
    for row in output:
        if row["input_fuel"] is None:
            row["input_fuel"] = ""

    return output


def cf_module_to_buildmodel(river_data):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])
    buildmodel = {
        "specified_demand_profile_cf": river_convert_sink.teo_demand_factor_group,
        "sets_technologies": cf_module_to_buildmodel_sets_technologies(river_data=river_data),
        "sets_fuels": cf_module_to_buildmodel_sets_fuels(river_data=river_data),
        "technologies_cf": cf_module_to_buildmodel_technologies_cf(river_data=river_data),
        "specified_annual_demand_cf": cf_module_to_buildmodel_specified_annual_demand_cf(river_data=river_data),
        "capacity_factor_cf": river_convert_source.teo_capacity_factor_group,
    }
    return buildmodel


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
            lambda name: create_default_technology(name=name),
            cf_module_to_buildmodel_sets_technologies(river_data=river_data),
        )
    )


def platform_to_buildmodel(initial_data, river_data):
    platform_technologies = platform_technologies_to_buildmodel(river_data=river_data)
    input_data = initial_data["input_data"]
    platform_sets = input_data["platform_sets"]
    platform_storages = input_data["platform_storages"]
    buildmodel = {
        "platform_technologies": platform_technologies,
        "platform_sets": platform_sets,
        "platform_storages": platform_storages,
        "platform_annual_emission_limit": input_data["platform_annual_emission_limit"],
        "platform_budget_limit": [
            {
                "Region": platform_sets["REGION"][0] if len(platform_sets["REGION"]) > 0 else None,
                "budget_limit": platform_sets["platform_budget_limit"]
            }
        ],
        "platform_technology_to_storage": [
            {
                "technology": storage.get("technology", "dhn"),
                "storage": storage["storage"],
                "technologytostorage": storage.get("technologytostorage", 1),
                "technologyfromstorage": storage.get("technologyfromstorage", 1),
            } for storage in platform_storages
        ],
    }
    return buildmodel
