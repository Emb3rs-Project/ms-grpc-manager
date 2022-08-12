import logging
import os
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm.session import Session

from reports.db_models import IntegrationReport, SimulationSession

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

DATABASE_URL = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(url=DATABASE_URL.format(
    user=os.getenv('PG_USERNAME'),
    password=os.getenv('PG_PASSWORD'),
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    db=os.getenv('PG_DATABASE'))
)


class Reporter:

    def __init__(self, session_uuid: str):
        self.session_uuid = session_uuid
        self.simulation_session = None
        self.__load_simulation()

    def __load_simulation(self):
        statement = select(SimulationSession).where(SimulationSession.simulation_uuid == self.session_uuid)
        with Session(engine) as session:
            self.simulation_session: SimulationSession = session.scalars(statement).one()

    def save_step_report(self, module: str, function: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        stmt = insert(IntegrationReport).values(
            simulation_id=self.simulation_session.simulation_id,
            simulation_uuid=self.simulation_session.simulation_uuid,
            step_uuid=str(uuid4()),
            data=input_data,
            output=output_data,
            module=module,
            function=function,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with engine.connect() as connection:
            with connection.begin():
                connection.execute(stmt)

    def save_step_error(self, module: str, function: str, input_data: Dict[str, Any], errors: Dict[str, Any]):
        stmt = insert(IntegrationReport).values(
            simulation_id=self.simulation_session.simulation_id,
            simulation_uuid=self.simulation_session.simulation_uuid,
            step_uuid=str(uuid4()),
            data=input_data,
            output={},
            errors=errors,
            module=module,
            function=function,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with engine.connect() as connection:
            with connection.begin():
                connection.execute(stmt)
