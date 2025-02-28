from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from typing import Optional
from datetime import datetime

def create_drilling_rig(db: Session, drilling_rig: schemas.DrillingRigCreate):
    db_drilling_rig = models.DrillingRig(
        address=drilling_rig.address,
        name=drilling_rig.name,
        status=drilling_rig.status,
        commissioning_date=drilling_rig.commissioning_date
    )
    db.add(db_drilling_rig)
    db.commit()
    db.refresh(db_drilling_rig)
    return db_drilling_rig

def create_robot(db: Session, robot: schemas.RobotCreate):
    db_robot = models.Robot(
        type=robot.type,
        identifier=robot.identifier,
        name=robot.name,
        operational=robot.operational,
        commissioning_date=robot.commissioning_date
    )
    db.add(db_robot)
    db.commit()
    db.refresh(db_robot)
    return db_robot

def create_work_execution(db: Session, work_execution: schemas.WorkExecutionCreate):
    db_work_execution = models.WorkExecution(
        robot_id=work_execution.robot_id,
        start_date=work_execution.start_date,
        end_date=work_execution.end_date,
        status=work_execution.status
    )
    db.add(db_work_execution)
    db.commit()
    db.refresh(db_work_execution)
    return db_work_execution

def create_work_plan(db: Session, work_plan: schemas.WorkPlanCreate):
    db_work_plan = models.WorkPlan(
        name=work_plan.name,
        type=work_plan.type,
        duration=work_plan.duration   
    )

    db.add(db_work_plan)
    db.commit()
    db.refresh(db_work_plan)
    return db_work_plan

def get_drilling_rig(db: Session, drilling_rig_id: int):
    drilling_rig = db.query(models.DrillingRig).filter(models.DrillingRig.id == drilling_rig_id).first()
    if drilling_rig is None:
        raise HTTPException(status_code=404, detail="Drilling rig not found")
    return drilling_rig

def get_filter_drilling_rigs(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(models.DrillingRig)

    if start_date:
        query = query.filter(models.DrillingRig.commissioning_date >= start_date)
    if end_date:
        query = query.filter(models.DrillingRig.commissioning_date <= end_date)

    return query.offset(skip).limit(limit).all()

def get_work_execution(db: Session, work_execution_id: int):
    return db.query(models.WorkExecution).filter(models.WorkExecution.id == work_execution_id).first()

def get_paused_work_executions(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.WorkExecution)
        .filter(models.WorkExecution.status == "paused")
        .offset(skip)
        .limit(limit)
        .all()
    )

def add_robot_to_drilling_rig(db: Session, robot_id: int, drilling_rig_id: int):
    robot = db.query(models.Robot).filter(models.Robot.id == robot_id).first()
    drilling_rig = db.query(models.DrillingRig).filter(models.DrillingRig.id == drilling_rig_id).first()

    if not robot:
        raise ValueError("Robot not found")
    if not drilling_rig:
        raise ValueError("Drilling rig not found")

    robot.drilling_rigs.append(drilling_rig)
    db.commit()
    db.refresh(robot)
    return robot

def add_robot_to_work_plan(db: Session, robot_id: int, work_plan_id: int):
    robot = db.query(models.Robot).filter(models.Robot.id == robot_id).first()
    work_plan = db.query(models.WorkPlan).filter(models.WorkPlan.id == work_plan_id).first()

    if not robot:
        raise ValueError("Robot not found")
    if not work_plan:
        raise ValueError("Work plan not found")

    robot.work_plans.append(work_plan)
    db.commit()
    db.refresh(robot)
    return robot