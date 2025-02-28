from pydantic import BaseModel
from datetime import date

class DrillingRigBase(BaseModel):
    address: str
    name: str
    status: bool
    commissioning_date: date

class DrillingRigCreate(DrillingRigBase):
    pass

class DrillingRig(DrillingRigBase):
    id: int

    class Config:
        orm_mode = True
        
class RobotBase(BaseModel):
    type: str
    identifier: str
    name: str
    operational: bool
    commissioning_date: date

class RobotCreate(RobotBase):
    pass

class Robot(RobotBase):
    id: int

    class Config:
        orm_mode = True

class WorkPlanBase(BaseModel):
    name: str
    type: str
    duration: int

class WorkPlanCreate(WorkPlanBase):
    pass

class WorkPlan(WorkPlanBase):
    id: int

    class Config:
        orm_mode = True

class WorkExecutionBase(BaseModel):
    robot_id: int
    start_date: date
    end_date: date
    status: str

class WorkExecutionCreate(WorkExecutionBase):
    pass

class WorkExecution(WorkExecutionBase):
    id: int

    class Config:
        orm_mode = True

class RobotDrillingRigLink(BaseModel):
    robot_id: int
    drilling_rig_id: int

class RobotWorkPlanLink(BaseModel):
    robot_id: int
    work_plan_id: int

class RobotData(BaseModel):
    commissioning_date: str
    usage_frequency: float