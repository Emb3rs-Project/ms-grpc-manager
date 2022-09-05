import json
from datetime import datetime
from random import randint
from typing import Dict
from uuid import uuid4

import pytest
from sqlalchemy.orm.session import Session

from config.settings import Settings
from reports.db_models import Base, engine, Simulation, SimulationSession


@pytest.fixture(scope="session", autouse=True)
def sqlalchemy_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def simulation_in_database(sqlalchemy_database) -> Simulation:
    fake_id = randint(9000, 9100)
    simulation = Simulation(
        id=fake_id,
        status="any",
        project_id=fake_id,
        simulation_metadata_id=fake_id,
        deleted_at=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    with Session(sqlalchemy_database) as session:
        session.add(simulation)
        session.commit()
        session.refresh(simulation)
    return simulation


@pytest.fixture(scope="session")
def simulation_session_in_database(sqlalchemy_database, simulation_in_database: Simulation) -> SimulationSession:
    simulation_uuid = str(uuid4())
    simulation_session = SimulationSession(
        id=randint(9101, 9200),
        simulation_uuid=simulation_uuid,
        simulation_id=simulation_in_database.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    with Session(sqlalchemy_database) as session:
        session.add(simulation_session)
        session.commit()
        session.refresh(simulation_session)
    return simulation_session


@pytest.fixture(scope="session")
def simulation_data() -> Dict:
    with open(f"{Settings.BASE_PATH}/tests/assets/simulation_data.json") as file:
        data = json.loads(file.read())
    return data
