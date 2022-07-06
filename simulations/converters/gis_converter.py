
## Create Network
from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel


def platform_to_create_network(initial_data):
    project_polygon = initial_data['project']['data']['polygon']
    input_data = initial_data['input_data']

    point_1 = project_polygon[0]
    point_2 = project_polygon[1]
    point_3 = [point_1[0], point_2[1]]
    point_4 = [point_2[1], point_1[0]]


    return {
        "polygon" : [point_1, point_2, point_3, point_4],
        "network_resolution" : input_data['network_resolution'],
        "ex_grid" : []
    }

def cf_module_to_create_network(river_data):
    river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data['convert_sink'])
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data['convert_source'])


    return {
        "n_demand_list" : river_convert_sink.n_demand_list,
        "n_supply_list" : river_convert_source.n_supply_list,
        "n_grid_specific" : {}
    }

def teo_module_to_create_netowrk(river_data):
    return {
        "ex_cap" : []
    }


## Optimize Network
def platform_to_optimize_network(initial_data):
    pass

def cf_module_to_optimize_network(river_data):
    pass

def teo_module_to_optimize_network(river_data):
    pass

def gis_module_to_optimize_network(river_data):
    pass