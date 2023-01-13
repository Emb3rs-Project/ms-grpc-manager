import pytest
from pytest_mock import MockerFixture

from config.settings import Settings
from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.demo_simulation import DemoSimulation


def test_demo_simulation_instance(simulation_session_in_database: SimulationSession):
    demo = DemoSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(demo, BaseSimulation)


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


def test_demo_simulation_run_with_iteration_between_gis_and_teo(
    simulation_session_in_database: SimulationSession, simulation_data: dict, mocker: MockerFixture,
):
    mocker.patch.object(Settings, "GIS_TEO_ITERATION_MODE", True)
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


@pytest.mark.xfail(reason="Gurobi not installed on the environment")
def test_demo_simulation_run_with_gurobi_solver(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["solver_gis"] = "GUROBI"
    simulation_data["initialData"]["solver_teo"] = "GUROBI"
    simulation_data["initialData"]["solver_market"] = "GUROBI"

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


def test_demo_simulation_run_with_scip_solver(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["solver_gis"] = "SCIP"
    simulation_data["initialData"]["solver_teo"] = "SCIP"
    simulation_data["initialData"]["solver_market"] = "SCIP"

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


def test_demo_simulation_run_with_highs_solver(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["solver_gis"] = "HIGHS"
    simulation_data["initialData"]["solver_teo"] = "HIGHS"
    simulation_data["initialData"]["solver_market"] = "HIGHS"

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


@pytest.mark.xfail(reason="COPT not installed on the environment")
def test_demo_simulation_run_with_copt_solver(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["solver_gis"] = "COPT"
    simulation_data["initialData"]["solver_teo"] = "COPT"
    simulation_data["initialData"]["solver_market"] = "COPT"

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


@pytest.mark.xfail(reason="Gurobi not installed on the environment")
def test_demo_simulation_run_with_multiple_solvers(
    simulation_session_in_database: SimulationSession, simulation_data: dict,
):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["solver_gis"] = "GUROBI"
    simulation_data["initialData"]["solver_teo"] = "SCIP"
    simulation_data["initialData"]["solver_market"] = "HIGHS"

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
