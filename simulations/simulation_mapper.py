
from typing import Dict
from simulations.demo_simulation import DemoSimulation
from simulations.orc_simulation import ORCSimulation


SIMULATION_MAPPER= {
  "demo_simulation" : DemoSimulation,
  "convert_orc" : ORCSimulation
}