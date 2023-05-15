from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.orc_simulation import ORCSimulation


def test_orc_simulation_instance(simulation_session_in_database: SimulationSession):
    orc = ORCSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(orc, BaseSimulation)
