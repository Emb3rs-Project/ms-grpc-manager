


from typing import Any, Dict

import jsonpickle
from cf.cf_models import ConvertSinkOutputModel, ConvertSourceOutputModel


def platform_to_convert_sink(initial_data):
  group_of_sinks = []

  for _sink in initial_data['sinks']:
    sink = _sink['values']
    sink['id'] = _sink['id']
    sink['consumer_type'] = 'non-household'
    sink['location'] = _sink['location']['data']['center']
    sink['streams'] = sink['characterization']['streams']

    group_of_sinks.append(sink)

  return {
    "group_of_sinks" : group_of_sinks
  }

def platform_to_convert_source(initial_data):
  group_of_sources = []

  for _source in initial_data['sources']:
    source = _source['values']['properties']
    source['id'] = _source['id']
    source['location'] = _source['location']['data']['center']
    source['streams'] = _source['values']['characterization']['streams']

    group_of_sources.append(source)

    return {
      "group_of_sources" : group_of_sources
    }

def cf_module_to_convert_source(initial_data: Dict[str, Any], river_data : Dict[str, Any]):

  river_convert_sink = ConvertSinkOutputModel().from_grpc(river_data['convert_sink'])
  
  output = {
    "sink_group_grid_supply_temperature": river_convert_sink.all_sinks_info['sink_group_grid_supply_temperature'],
    "sink_group_grid_return_temperature": river_convert_sink.all_sinks_info['sink_group_grid_return_temperature']
  }  
  
  if river_data.get('convert_source') is not None:
    river_convert_source = ConvertSourceOutputModel().from_grpc(river_data['convert_source'])
    output['last_iteration_data'] = river_convert_source.dict()

  return output


def platform_to_orc_convert(initial_data):
  convert_source = platform_to_convert_source(initial_data=initial_data)
  output = convert_source["group_of_sources"][0]
  
  return convert_source["group_of_sources"][0]
