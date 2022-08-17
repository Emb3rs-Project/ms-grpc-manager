from typing import Dict

import pytest
from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.demo_simulation import DemoSimulation


def test_demo_simulation_instance(simulation_session_in_database):
    demo = DemoSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(demo, BaseSimulation)


@pytest.mark.demo
def test_demo_simulation_run(simulation_session_in_database: SimulationSession, simulation_data: Dict):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    demo = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
    )

    assert demo.run() is None
