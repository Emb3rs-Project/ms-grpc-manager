from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    simulation_metadata_id = Column(Integer)
    name = Column(String)
    status = Column(String)
    extra = Column(JSON)
    sessions = relationship("SimulationSession", back_populates="simulation")
    reports = relationship("IntegrationReport", back_populates="simulation")
    results = relationship("SimulationResult", back_populates="simulation")
    deleted_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self) -> str:
        return (
            f"Simulation(id={self.id!r},project_id={self.project_id!r},"
            f"simulation_metadata_id={self.simulation_metadata_id!r}, name={self.name!r},extra={self.extra!r})"
        )


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"

    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    simulation_uuid = Column(String)
    simulation = relationship("Simulation", back_populates="sessions")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self) -> str:
        return (
            f"SimulationSession(id={self.id!r}, simulation_id={self.simulation_id!r}, "
            f"simulation_uuid={self.simulation_uuid!r}), simulation={self.simulation!r}"
        )


class IntegrationReport(Base):
    __tablename__ = "integration_reports"

    id = Column(Integer, primary_key=True)

    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    simulation_uuid = Column(String)
    step_uuid = Column(String)
    data = Column(JSON)
    output = Column(JSON)
    errors = Column(JSON)
    module = Column(String)
    function = Column(String)
    simulation = relationship("Simulation", back_populates="reports")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self) -> str:
        return (
            f"IntegrationReport(id={self.id!r}, simulation={self.simulation!r}, data={self.data!r}, "
            f"module={self.module!r}, errors={self.errors!r}, step_uuid={self.step_uuid!r})"
        )


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    simulation = relationship("Simulation", back_populates="results")
    simulation_uuid = Column(String)
    data = Column(JSON)

    def __repr__(self) -> str:
        return f"IntegrationReport(id={self.id!r}, simulation={self.simulation!r}, data={self.data!r})"


class Instance(Base):
    __tablename__ = "instances"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    values = Column(JSON)
