from enum import Enum
from datetime import  datetime
from typing import List, Optional, Union, Any
from bson import ObjectId
from .customPydantic import PydanticObjectId
from pydantic import BaseModel
from .param_schema import RunParameter


RUNS_COLLECTION = 'runs'


class RunStatusEnum(str, Enum):
    in_progress = "in_progress"
    new = "new"
    done = "done"
    error = "error"


class DBricksRun(BaseModel):
    """Databricks models"""
    model_id: Union[str, PydanticObjectId]
    user_name: str
    date: datetime  # data bricks workspace
    status: Optional[RunStatusEnum] = RunStatusEnum.new
    parameters: List[RunParameter] = []
    run_id: Optional[int] = 0
    number_in_job: Optional[int] = 0
    files_names: Optional[Any] = None


class DBricksRunResponse(DBricksRun):
    id: Optional[str] = '0'

    async def update_status(self, mongo_instance, status: RunStatusEnum):
        self.status = status
        modelruns = mongo_instance[RUNS_COLLECTION]
        modelruns.update_one({"_id": ObjectId(self.id)}, {"$set": {"status": self.status}})

    async def set_run_id(self, mongo_instance, run_id: int, number_in_job: int):
        self.run_id = run_id
        self.number_in_job = number_in_job
        modelruns = mongo_instance[RUNS_COLLECTION]
        modelruns.update_one({"_id": ObjectId(self.id)},
                             {"$set": {
                                 "run_id": self.run_id,
                                 "number_in_job": self.number_in_job
                             }})
