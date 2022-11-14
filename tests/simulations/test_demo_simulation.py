import pytest

from config.settings import Solver
from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.demo_simulation import DemoSimulation


def test_demo_simulation_instance(simulation_session_in_database: SimulationSession):
    demo = DemoSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(demo, BaseSimulation)


@pytest.mark.demo
def test_demo_simulation_run(simulation_session_in_database: SimulationSession, simulation_data: dict):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    demo = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
    )

    assert demo.run() is None
    assert demo.river_data.get("convert_sink") is not None
    assert demo.river_data.get("convert_source") is not None
    assert demo.river_data.get("create_network") is not None
    assert demo.river_data.get("optimize_network") is not None
    assert demo.river_data.get("buildmodel") is not None
    assert demo.river_data.get("long_term") is not None
    assert demo.river_data.get("feasability") is not None


@pytest.mark.demo
def test_demo_simulation_run_with_simulation_steps(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_steps = ["convert_sink", "convert_source"]
    demo = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
        simulation_steps=simulation_steps,
    )

    assert demo.run() is None
    assert demo.river_data.get("convert_sink") is not None
    assert demo.river_data.get("convert_source") is not None
    assert demo.river_data.get("create_network") is None
    assert demo.river_data.get("optimize_network") is None
    assert demo.river_data.get("buildmodel") is None
    assert demo.river_data.get("long_term") is None
    assert demo.river_data.get("feasability") is None


@pytest.mark.demo
def test_demo_simulation_run_with_invalid_simulation_steps_should_raise_exception(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_steps = ["any_simulation_that_not_exist"]
    demo = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
        simulation_steps=simulation_steps,
    )

    with pytest.raises(Exception) as exc:
        demo.run()

    assert str(exc.value) == "Step 'any_simulation_that_not_exist' not exist for this simulation"


@pytest.mark.demo
def test_demo_simulation_run_with_scip_solver(simulation_session_in_database: SimulationSession, simulation_data: dict):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    demo = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
        simulation_solver=Solver.SCIP,
    )

    assert demo.run() is None
    assert demo.river_data.get("convert_sink") is not None
    assert demo.river_data.get("convert_source") is not None
    assert demo.river_data.get("create_network") is not None
    assert demo.river_data.get("optimize_network") is not None
    assert demo.river_data.get("buildmodel") is not None
    assert demo.river_data.get("long_term") is not None
    assert demo.river_data.get("feasability") is not None
