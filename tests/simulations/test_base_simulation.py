import pytest
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from config.settings import Settings, Solver
from reports.db_models import IntegrationReport, SimulationSession
from simulations.base_simulation import BaseSimulation
from simulations.old_base_simulation import OldBaseSimulation


def test_base_simulation_inheritance(simulation_session_in_database: SimulationSession):
    class FakeSimulation(BaseSimulation):
        def _run(self):
            pass

    base = FakeSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)

    assert base.initial_data == {}
    assert base.simulation_session == simulation_session_in_database.simulation_uuid
    assert base.simulation_steps is None
    assert base.simulation_solver == Settings.DEFAULT_SIMULATION_SOLVER
    assert isinstance(base.simulation_solver, Solver)


def test_base_simulation_inheritance_without_implement_all_abstract_methods():
    class FakeSimulation(BaseSimulation):  # noqa
        pass

    with pytest.raises(TypeError) as exc:
        FakeSimulation(initial_data={}, simulation_session="any")

    assert str(exc.value) == "Can't instantiate abstract class FakeSimulation with abstract method _run"


def test_old_base_simulation_inheritance(sqlalchemy_database, simulation_session_in_database: SimulationSession):
    class FakeSimulation(OldBaseSimulation):
        pass

    base = FakeSimulation(initial_data={}, simulation_session=simulation_session_in_database.simulation_uuid)
    base.run()

    stmt = (
        select(IntegrationReport)
        .where(IntegrationReport.simulation_uuid == simulation_session_in_database.simulation_uuid)
    )
    with Session(sqlalchemy_database) as session:
        result = session.scalars(stmt).all()

    assert len(result) > 0
    assert base.initial_data == {}
    assert base.simulation_session == simulation_session_in_database.simulation_uuid
