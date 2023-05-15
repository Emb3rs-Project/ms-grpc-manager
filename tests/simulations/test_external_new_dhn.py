from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.external_new_dhn import ExternalNewDHN


def test_external_new_dhn_instance(simulation_session_in_database: SimulationSession):
    dhn = ExternalNewDHN(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(dhn, BaseSimulation)
