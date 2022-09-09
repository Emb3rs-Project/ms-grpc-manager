from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel
from gis.gis_models import CreateNetworkOutputModel
from teo.teo_models import BuildModelOutputModel


def platform_to_create_network(initial_data):
    project_polygon = initial_data["project"]["data"]["polygon"]
    input_data = initial_data["input_data"]

    point_1 = project_polygon[0]
    point_2 = project_polygon[1]
    point_3 = [point_1[0], point_2[1]]
    point_4 = [point_2[0], point_1[1]]

    create_network = {
        "polygon": [point_1, point_2, point_3, point_4],
        "network_resolution": input_data["network_resolution"],
        "ex_grid": input_data.get("ex_grid", []),
    }
    return create_network


def cf_module_to_create_network(river_data):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])
    create_network = {
        "n_demand_list": river_convert_sink.n_demand_list,
        "n_supply_list": river_convert_source.n_supply_list,
        "n_grid_specific": river_convert_sink.n_grid_specific,
    }
    return create_network


def teo_module_to_create_network(river_data):
    return {"ex_cap": []}


def platform_to_optimize_network(initial_data):
    input_data = initial_data["input_data"]
    optimize_network = {
        "network_resolution": input_data["network_resolution"],
        "water_den": input_data["water_den"],
        "factor_street_terrain": input_data["factor_street_terrain"],
        "factor_street_overland": input_data["factor_street_overland"],
        "heat_capacity": input_data["heat_capacity"],
        "flow_temp": input_data["flow_temp"],
        "return_temp": input_data["return_temp"],
        "ground_temp": input_data["ground_temp"],
        "ambient_temp": input_data["ambient_temp"],
        "fc_dig_st": input_data["fc_dig_st"],
        "vc_dig_st": input_data["vc_dig_st"],
        "vc_dig_st_ex": input_data["vc_dig_st_ex"],
        "fc_dig_tr": input_data["fc_dig_tr"],
        "vc_dig_tr": input_data["vc_dig_tr"],
        "vc_dig_tr_ex": input_data["vc_dig_tr_ex"],
        "fc_pip": input_data["fc_pip"],
        "vc_pip": input_data["vc_pip"],
        "vc_pip_ex": input_data["vc_pip_ex"],
        "invest_pumps": input_data["invest_pumps"],
        # NEW - Check if this should be in Platform.
        "surface_losses_dict": input_data.get("surface_losses_dict", [{"dn": 1.0, "overland_losses": 1.0}])
        # NEW
    }
    return optimize_network


def cf_module_to_optimize_network(river_data):
    # IF OK TURN CREATE AND OPTIMIZE TO ONE
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data["convert_sink"])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data["convert_source"])
    optimize_network = {
        "n_demand_list": river_convert_sink.n_demand_list,
        "n_supply_list": river_convert_source.n_supply_list,
    }
    return optimize_network


def teo_module_to_optimize_network(river_data):
    optimize_network = {"ex_cap": []}
    if buildmodel := river_data.get("buildmodel"):
        river_buildmodel = BuildModelOutputModel().from_grpc(buildmodel)
        optimize_network["ex_cap"] = river_buildmodel["ex_capacities"]
    return optimize_network


def gis_module_to_optimize_network(initial_data, river_data):
    river_create_network = CreateNetworkOutputModel().from_grpc(river_data["create_network"])
    return river_create_network.dict()
