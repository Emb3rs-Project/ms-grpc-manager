from typing import Type, Dict

from simulations.base_simulation import BaseSimulation
from simulations.demo_simulation import DemoSimulation
from simulations.external_new_dhn import ExternalNewDHN
from simulations.orc_simulation import ORCSimulation
from simulations.pinch_simulation import PinchSimulation

SIMULATION_MAPPER: Dict[str, Type[BaseSimulation]] = {
    "demo_simulation": DemoSimulation,
    "convert_orc": ORCSimulation,
    "external_new_dhn": ExternalNewDHN,
    "pinch_simulation": PinchSimulation,
}
