from uuid import uuid4
from typing import List, Optional
from pydantic import BaseModel
from .param_schema import Parameter


MODELS_COLLECTION = 'models'


class DBricksModel(BaseModel):
    """Databricks models"""
    name: Optional[str] = 'model-' + str(uuid4())
    workspace: str  # data bricks workspace
    notebook_name: str
    cluster_name: str
    token: str  # data bricks token
    parameters: List[Parameter] = []
    output_path: Optional[str] = 'notebook'  # dashboard name to export
    job_id: Optional[int] = None

    def format_data(self):
        self.cluster_name = self.cluster_name.lower().strip()
        self.workspace = self.workspace.lower().strip()
        self.token = self.token.strip()
        if self.output_path is not None:
            self.output_path = self.output_path.strip()

        self.workspace = self.workspace[:-1] \
            if self.workspace[-1] == '/' else self.workspace

        if 'http://' in self.workspace:
            self.workspace.replace('http://', 'https://')
        # TODO: regext to check workspace

    def validate_parameters(self):
        for param in self.parameters:
            if param.is_file and (param.conn_str is None or param.container_name is None):
                return False
            if param.is_file:
                param.folder = param.default
                param.default = None
        return True


class DBricksModelResponse(DBricksModel):
    id: Optional[str] = '0'


class DBricksModelsResponse(BaseModel):
    models: List[DBricksModelResponse]
