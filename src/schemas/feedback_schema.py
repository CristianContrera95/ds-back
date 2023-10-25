from datetime import datetime
from typing import List, Optional, Union
from .customPydantic import PydanticObjectId
from pydantic import BaseModel


FEEDBACK_COLLECTION = 'feedback'


class RunFeedBack(BaseModel):
    """Databricks models"""
    run_id: Union[str, PydanticObjectId]
    author: str
    date: datetime  # data bricks workspace
    msg: str
    files: Optional[List[str]] = []


class RunFeedBackResponse(RunFeedBack):
    id: Optional[str] = '0'
