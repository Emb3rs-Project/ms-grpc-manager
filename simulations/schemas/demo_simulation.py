from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ItermediateStep(Enum):
    GIS_OPTIMIZE_NETWORK = "optimize_network"
    TEO_BUILDMODEL = "buildmodel"


class SimulationData(BaseModel):
    itermediate_step: ItermediateStep
    simulation_session: str
    simulation_steps: Optional[list]
    initial_data: dict
    river_data: dict
