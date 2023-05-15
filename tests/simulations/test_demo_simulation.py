import pytest
from pytest_mock import MockerFixture
from redis import ConnectionError

from config.redis_client import RedisClient
from config.settings import Settings
from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.demo_simulation import DemoSimulation


def test_demo_simulation_instance(simulation_session_in_database: SimulationSession):
    demo = DemoSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(demo, BaseSimulation)


def test_demo_simulation_run(simulation_session_in_database: SimulationSession, simulation_data: dict):
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["intermediate_steps"] = False

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


def test_demo_simulation_run_when_invalid_simulation_steps_should_raise_exception(
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


@pytest.mark.xfail(reason="Redis unavailable", raises=ConnectionError)
def test_demo_simulation_run_with_intermediate_steps(
    simulation_session_in_database: SimulationSession, simulation_data: dict, mocker: MockerFixture,
):
    mocker.patch.object(Settings, "GIS_TEO_ITERATION_MODE", True)
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["intermediate_steps"] = True
    redis = RedisClient()

    demo_start = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
    )
    assert demo_start.run() is None
    assert demo_start.river_data.get("convert_sink") is not None
    assert demo_start.river_data.get("convert_source") is not None
    assert demo_start.river_data.get("create_network") is not None
    assert demo_start.river_data.get("optimize_network") is not None
    assert demo_start.river_data.get("buildmodel_platform_input") is not None
    assert demo_start.river_data.get("buildmodel") is None
    assert demo_start.river_data.get("long_term") is None
    assert demo_start.river_data.get("feasability") is None

    # GIS Intermediate Step Flow
    # total_costs_update_value = 2000000.10
    # demo_gis_redis_data = redis.get(simulation_session=simulation_session_in_database.simulation_uuid)
    # network_solution_edges = demo_gis_redis_data.river_data["optimize_network"]["network_solution_edges"]
    # network_solution_edges[0]["total_costs"] = total_costs_update_value
    # demo_gis_update = DemoSimulation(
    #     update_data={"optimize_network": {"network_solution_edges": network_solution_edges}},
    #     simulation_session=simulation_session_in_database.simulation_uuid,
    # )
    # assert demo_gis_update.run_update() is None
    # assert demo_gis_update.river_data.get("optimize_network") is not None
    # assert demo_gis_update.river_data.get("buildmodel") is None
    # post_updated_network_solution_edges = demo_gis_update.river_data["optimize_network"]["network_solution_edges"]
    # assert post_updated_network_solution_edges[0]["total_costs"] == total_costs_update_value

    max_capacity_investment_update_value = 10005000000
    demo_teo_redis_data = redis.get(simulation_session=simulation_session_in_database.simulation_uuid)
    platform_technologies = demo_teo_redis_data.river_data["buildmodel_platform_input"]["platform_technologies"]
    platform_technologies[0]["max_capacity_investment"] = max_capacity_investment_update_value

    demo_teo_update = DemoSimulation(
        update_data={"buildmodel": {"platform_technologies": platform_technologies}},
        simulation_session=simulation_session_in_database.simulation_uuid,
    )
    assert demo_teo_update.run_update() is None
    assert demo_teo_update.river_data.get("convert_sink") is not None
    assert demo_teo_update.river_data.get("convert_source") is not None
    assert demo_teo_update.river_data.get("create_network") is not None
    assert demo_teo_update.river_data.get("optimize_network") is not None
    assert demo_teo_update.river_data.get("buildmodel_platform_input") is not None
    assert demo_teo_update.river_data.get("buildmodel") is not None
    assert demo_teo_update.river_data.get("long_term") is not None
    assert demo_teo_update.river_data.get("feasability") is not None

    post_upd_platform_technologies = demo_teo_update.river_data["buildmodel_platform_input"]["platform_technologies"]
    assert post_upd_platform_technologies[0]["max_capacity_investment"] == max_capacity_investment_update_value

    report_steps = {
        index: (step.module, step.function, step.errors)
        for index, step in enumerate(demo_teo_update.reporter.get_steps())
    }
    assert report_steps


@pytest.mark.xfail(reason="Redis unavailable", raises=ConnectionError)
def test_demo_simulation_run_intermediate_steps_when_has_some_error_on_module(
    simulation_session_in_database: SimulationSession, simulation_data: dict, mocker: MockerFixture,
):
    mocker.patch.object(Settings, "GIS_TEO_ITERATION_MODE", True)
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["intermediate_steps"] = True
    RedisClient()

    demo_start = DemoSimulation(
        initial_data=simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
    )
    assert demo_start.run() is None
    assert demo_start.river_data.get("convert_sink") is not None
    assert demo_start.river_data.get("convert_source") is not None
    assert demo_start.river_data.get("create_network") is not None
    assert demo_start.river_data.get("optimize_network") is not None
    assert demo_start.river_data.get("buildmodel") is None
    platform_technologies = demo_start.river_data["buildmodel_platform_input"]["platform_technologies"]

    demo_teo_update = DemoSimulation(
        update_data={"buildmodel": {"platform_technologies": platform_technologies}},
        simulation_session=simulation_session_in_database.simulation_uuid,
    )
    mocker.patch.object(demo_teo_update.gis, "create_network", side_effect=Exception("mocked error"))
    assert demo_teo_update.run_update() is None
    assert demo_teo_update.river_data.get("optimize_network") is not None
    assert demo_teo_update.river_data.get("buildmodel") is not None
    assert demo_teo_update.river_data.get("long_term") is None
    assert demo_teo_update.river_data.get("feasability") is None

    report_steps = {
        index: (step.module, step.function, step.errors)
        for index, step in enumerate(demo_teo_update.reporter.get_steps())
    }
    assert report_steps


def test_demo_simulation_run_with_iteration_between_gis_and_teo(
    simulation_session_in_database: SimulationSession, simulation_data: dict, mocker: MockerFixture,
):
    mocker.patch.object(Settings, "GIS_TEO_ITERATION_MODE", True)
    simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    simulation_data["initialData"]["intermediate_steps"] = False

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
    simulation_data["initialData"]["intermediate_steps"] = False
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
    simulation_data["initialData"]["intermediate_steps"] = False
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
    simulation_data["initialData"]["intermediate_steps"] = False
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
    simulation_data["initialData"]["intermediate_steps"] = False
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
    simulation_data["initialData"]["intermediate_steps"] = False
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
