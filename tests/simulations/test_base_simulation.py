import pytest

from reports.db_models import SimulationSession
from simulations.base_simulation import BaseSimulation


def test_base_simulation_inheritance(simulation_session_in_database: SimulationSession):
    class FakeSimulation(BaseSimulation):
        def _run(self):
            pass

    base = FakeSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)

    assert base.initial_data == {}
    assert base.simulation_session == simulation_session_in_database.simulation_uuid
    assert base.simulation_steps is None


def test_base_simulation_inheritance_without_implement_all_abstract_methods():
    class FakeSimulation(BaseSimulation):  # noqa
        pass

    with pytest.raises(TypeError) as exc:
        FakeSimulation(initial_data={}, simulation_session="any")

    assert str(exc.value) == "Can't instantiate abstract class FakeSimulation with abstract method _run"
