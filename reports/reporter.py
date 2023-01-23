import logging
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy import select, insert
from sqlalchemy.orm.session import Session

from reports.db_models import IntegrationReport, SimulationSession, engine

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class Reporter:

    def __init__(self, session_uuid: str) -> None:
        self.session_uuid = session_uuid
        self.simulation_session = None
        self.__load_simulation()

    def save_step_report(
        self, module: str, function: str, input_data: Dict[str, Any], output_data: Dict[str, Any]
    ) -> None:
        statement = insert(IntegrationReport).values(
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
        with Session(engine) as session:
            session.execute(statement)
            session.commit()

    def save_step_error(self, module: str, function: str, input_data: Dict[str, Any], errors: Dict[str, Any]) -> None:
        statement = insert(IntegrationReport).values(
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
        with Session(engine) as session:
            session.execute(statement)
            session.commit()

    def get_steps(self) -> list[IntegrationReport]:
        statement = select(IntegrationReport).where(
            IntegrationReport.simulation_id == self.simulation_session.simulation_id
        )
        with Session(engine) as session:
            return session.execute(statement).scalars().all()

    def __load_simulation(self) -> None:
        statement = select(SimulationSession).where(SimulationSession.simulation_uuid == self.session_uuid)
        with Session(engine) as session:
            self.simulation_session: SimulationSession = session.scalars(statement).one()
