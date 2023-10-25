from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks
from api.views.login import get_current_account
from schemas import (
    DBricksModel,
    DBricksModelResponse,
    DBricksRun,
    DBricksRunResponse,
    RunFeedBack,
    RunFeedBackResponse
)
from core.models import (
    get_model_list,
    save_model,
    update_model,
    delete_model,
    get_runs_list,
    save_run,
    save_feedback,
    get_feedback,
    get_params_storage_sas,
    export_results,
    remove_tmpfile
)
from core.storage.api import get_feedback_sas


router = APIRouter(dependencies=[Depends(get_current_account)])


# Models
@router.get("/", response_model=List[DBricksModelResponse], description="Returns the model list")
async def get_models():
    return await get_model_list()


@router.post("/", description="Create a new model")
async def new_model(model: DBricksModel):
    model = await save_model(model)
    return {"model_id": str(model.id)}


@router.patch("/", description="Update a model")
async def edit_model(model: DBricksModelResponse):
    model = await update_model(model)
    return {"model_id": str(model.id)}


@router.delete("/{model_uid}", description="Update a model")
async def drop_model(model_uid: str):
    model = await delete_model(model_uid)
    return {"delete": str(model.id)}


@router.get("/storage_sas", description="Get token sas")
async def get_feedback_storage_sas():
    return {"storage_sas": await get_feedback_sas()}


@router.get("/{model_uid}/storage_sas", description="Get token sas from model")
async def get_param_storage_sas(model_uid: str):
    return {"storage_sas": await get_params_storage_sas(model_uid)}


# Models runs
@router.get("/{model_uid}/runs", response_model=List[DBricksRunResponse],
            description="Returns the model runs list")
async def get_runs(model_uid: str):
    return await get_runs_list(model_uid)


@router.post("/{model_uid}/runs", description="Create new run")
async def new_run(run: DBricksRun):
    run = await save_run(run)
    return {"run_id": run.id}


@router.post("/{model_uid}/feedback", description="Set a feedback")
async def set_feed_back(feedback: RunFeedBack):
    feedback = await save_feedback(feedback)
    return {"feedback_id": feedback.id}


@router.get("/{model_uid}/feedback/{run_uid}", response_model=List[RunFeedBackResponse],
            description="get feedback list")
async def get_feed_back(run_uid: str = '0'):
    return await get_feedback(run_uid)


@router.get("/{model_uid}/runs/export", description="Download run results")
async def export_run_results(model_uid: str, run_id: str = 0, dbricks_run_id: int = 0):
    tmp_path = await export_results(model_uid, run_id, dbricks_run_id)
    tasks = BackgroundTasks()
    tasks.add_task(remove_tmpfile, tmp_path)  # remove tmp file after response returns
    return FileResponse(tmp_path, media_type="octet/stream", background=tasks)
