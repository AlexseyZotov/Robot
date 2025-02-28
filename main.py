from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, crud, schemas, data
from .cache import cache_get, cache_set
from datetime import datetime
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import base64


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/drilling_rigs/filter", response_model=list[schemas.DrillingRig])
def filter_drilling_rigs(
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    drilling_rigs = crud.get_filter_drilling_rigs(
        db=db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    return drilling_rigs

@app.get("/drilling_rigs/{drilling_rig_id}", response_model=schemas.DrillingRig)
def read_drilling_rig(drilling_rig_id: int, db: Session = Depends(get_db)):
    cached_drilling_rig = cache_get(f"drilling_rig_{drilling_rig_id}")
    if cached_drilling_rig:
        return schemas.DrillingRig.parse_raw(cached_drilling_rig)

    drilling_rig = crud.get_drilling_rig(db=db, drilling_rig_id=drilling_rig_id)
    if drilling_rig is None:
        raise HTTPException(status_code=404, detail="drilling_rig not found")

    drilling_rig_pydantic = schemas.DrillingRig.from_orm(drilling_rig)
    cache_set(f"drilling_rig_{drilling_rig_id}", drilling_rig_pydantic.json())
    return drilling_rig_pydantic

@app.get("/work_execution/paused", response_model=list[schemas.WorkExecution])
def read_paused_work_executions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    paused_work_executions = crud.get_paused_work_executions(db=db, skip=skip, limit=limit)
    return paused_work_executions

@app.post("/drilling_rigs/", response_model=schemas.DrillingRig)
def create_drilling_rig(drilling_rig: schemas.DrillingRigCreate, db: Session = Depends(get_db)):
    return crud.create_drilling_rig(db=db, drilling_rig=drilling_rig)

@app.post("/robots/", response_model=schemas.Robot)
def create_robot(robot: schemas.RobotCreate, db: Session = Depends(get_db)):
    return crud.create_robot(db=db, robot=robot)

@app.post("/work_executions/", response_model=schemas.WorkExecution)
def create_work_execution(work_execution: schemas.WorkExecutionCreate, db: Session = Depends(get_db)):
    return crud.create_work_execution(db=db, work_execution=work_execution)

@app.post("/work_plans/", response_model=schemas.WorkPlan)
def create_work_plan(work_plan: schemas.WorkPlanCreate, db: Session = Depends(get_db)):
    return crud.create_work_plan(db=db, work_plan=work_plan)

@app.put("/work_executions/{work_execution_id}", response_model=schemas.WorkExecution)
def update_or_create_work_execution(
    work_execution_id: int,
    work_execution: schemas.WorkExecutionCreate,
    db: Session = Depends(get_db)
):
    db_work_execution = crud.get_work_execution(db, work_execution_id=work_execution_id)

    if db_work_execution:
        db_work_execution.start_date = work_execution.start_date
        db_work_execution.end_date = work_execution.end_date
        db_work_execution.status = work_execution.status
        db_work_execution.robot_id = work_execution.robot_id
    else:
        db_work_execution = models.WorkExecution(
            id=work_execution_id,  
            start_date=work_execution.start_date,
            end_date=work_execution.end_date,
            status=work_execution.status,
            robot_id=work_execution.robot_id
        )
        db.add(db_work_execution)

    db.commit()
    db.refresh(db_work_execution)
    return db_work_execution

@app.post("/robots/link_to_drilling_rig", response_model=schemas.Robot)
def link_robot_to_drilling_rig(link_request: schemas.RobotDrillingRigLink, db: Session = Depends(get_db)):
    robot = crud.add_robot_to_drilling_rig(db, robot_id=link_request.robot_id, drilling_rig_id=link_request.drilling_rig_id)
    return robot

@app.post("/robots/link_to_work_plan", response_model=schemas.Robot)
def link_robot_to_work_plan_id(link_request: schemas.RobotWorkPlanLink, db: Session = Depends(get_db)):
    robot = crud.add_robot_to_work_plan(db, robot_id=link_request.robot_id, work_plan_id=link_request.work_plan_id)
    return robot

@app.post("/predict")
def predict_failure(robot_data: schemas.RobotData):
    try:
        commissioning_date = pd.to_datetime(robot_data.commissioning_date)

        days_until_failure = data.model.predict([[robot_data.usage_frequency]])[0]

        predicted_failure_date = commissioning_date + pd.Timedelta(days=days_until_failure)

        return {
            "predicted_failure_date": predicted_failure_date.strftime("%Y-%m-%d"),
            "days_until_failure": int(days_until_failure)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/visualize")
def visualize():
    try:
        robots = [
            {"commissioning_date": "2020-01-01", "usage_frequency": 10},
            {"commissioning_date": "2021-03-15", "usage_frequency": 20},
            {"commissioning_date": "2019-07-20", "usage_frequency": 15},
            {"commissioning_date": "2022-05-10", "usage_frequency": 25},
        ]

        predictions = []
        for robot in robots:
            commissioning_date = pd.to_datetime(robot["commissioning_date"])
            days_until_failure = data.model.predict([[robot["usage_frequency"]]])[0]
            predicted_failure_date = commissioning_date + pd.Timedelta(days=days_until_failure)
            predictions.append({
                "commissioning_date": robot["commissioning_date"],
                "usage_frequency": robot["usage_frequency"],
                "predicted_failure_date": predicted_failure_date.strftime("%Y-%m-%d"),
                "days_until_failure": int(days_until_failure)
            })

        df = pd.DataFrame(predictions)

        plt.figure(figsize=(10, 6))
        plt.bar(df["commissioning_date"], df["days_until_failure"], color='blue')
        plt.xlabel("Дата ввода в эксплуатацию")
        plt.ylabel("Дней до выхода из строя")
        plt.title("Предсказание выхода из строя роботов")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_path = "failure_prediction_plot.png"
        plt.savefig(plot_path)
        plt.close()

        with open(plot_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

        return HTMLResponse(content=f"""
            <h1>Результаты предсказания</h1>
            <h2>График</h2>
            <img src="data:image/png;base64,{image_base64}" alt="График">
            <h2>Таблица</h2>
            {df.to_html(index=False)}
        """)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))