import pytest
from pytest_mock import MockerFixture

from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.pinch_simulation import PinchSimulation


def test_pinch_simulation_instance(simulation_session_in_database: SimulationSession):
    pinch = PinchSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    assert isinstance(pinch, BaseSimulation)


@pytest.mark.pinch
def test_pinch_simulation_run(
    simulation_session_in_database: SimulationSession, pinch_simulation_data: dict,
):
    pinch_simulation_data["simulationUuid"] = simulation_session_in_database.simulation_uuid
    pinch = PinchSimulation(
        initial_data=pinch_simulation_data["initialData"],
        simulation_session=simulation_session_in_database.simulation_uuid,
    )

    assert pinch.run() is None
    assert pinch.river_data.get("convert_pinch") is not None


@pytest.mark.pinch
def test_pinch_simulation_run_with_mocked_input_data(
    simulation_session_in_database: SimulationSession, convert_pinch_input_data: dict, mocker: MockerFixture,
):
    mock = mocker.patch("simulations.pinch_simulation.platform_to_convert_pinch", return_value=convert_pinch_input_data)
    pinch = PinchSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)

    assert pinch.run() is None
    assert pinch.river_data.get("convert_pinch") is not None

    mock.reset_mock()
