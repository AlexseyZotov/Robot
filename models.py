from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Table
from .database import Base
from sqlalchemy.orm import relationship

robot_drilling_rig_association = Table(
    'robot_drilling_rig_association', Base.metadata,
    Column('robot_id', Integer, ForeignKey('robots.id'), primary_key=True),
    Column('drilling_rig_id', Integer, ForeignKey('drilling_rigs.id'), primary_key=True)
)

robot_work_plan_association = Table(
    'robot_work_plan_association', Base.metadata,
    Column('robot_id', Integer, ForeignKey('robots.id'), primary_key=True),
    Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True)
)

class DrillingRig(Base):
    __tablename__ = 'drilling_rigs'
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(Boolean, nullable=False)
    commissioning_date = Column(Date, nullable=False)
    robots = relationship("Robot", secondary=robot_drilling_rig_association, back_populates="drilling_rigs")

class Robot(Base):
    __tablename__ = 'robots'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    identifier = Column(String, nullable=False)
    name = Column(String, nullable=False)
    operational = Column(Boolean, nullable=False)
    commissioning_date = Column(Date, nullable=False)
    drilling_rigs = relationship("DrillingRig", secondary=robot_drilling_rig_association, back_populates="robots")
    work_plans = relationship("WorkPlan", secondary=robot_work_plan_association, back_populates="robots")
    work_executions = relationship("WorkExecution", back_populates="robot")

class WorkPlan(Base):
    __tablename__ = 'work_plans'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    robots = relationship("Robot", secondary=robot_work_plan_association, back_populates="work_plans")

class WorkExecution(Base):
    __tablename__ = 'work_executions'
    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey('robots.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    robot = relationship("Robot", back_populates="work_executions")