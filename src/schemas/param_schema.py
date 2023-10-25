from typing import Optional, List
from pydantic import BaseModel


class Parameter(BaseModel):
    """Model parameters for data bricks"""
    name: str
    default: Optional[str] = None
    is_file: Optional[bool] = False
    conn_str: Optional[str] = None
    container_name: Optional[str] = None
    folder: Optional[str] = None
    regexp_format: Optional[str] = None


class ParameterResponse(BaseModel):
    """Model parameters for data bricks"""
    name: str
    default: Optional[str] = None
    is_file: Optional[bool] = False
    container_name: Optional[str] = None
    folder: Optional[str] = None
    regexp_format: Optional[str] = None


class ModelParameters(BaseModel):
    """Model parameters for data bricks"""
    parameters: List[Parameter]


class RunParameter(BaseModel):
    """Model parameters for data bricks"""
    name: str
    value: str
