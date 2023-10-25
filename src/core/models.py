import os
import traceback
from typing import List

import pymongo
from bson import ObjectId
from pydantic import parse_obj_as
from requests.exceptions import HTTPError

from api import mongodb, logger
from db.mongo import convert_id_field_collection, format_parameters
from core.databricks import (
    create_job,
    update_job,
    delete_job,
    export_job_results
)
from core.storage import get_param_sas
from core.databricks import utils, exceptions
from core.job_thread import JOB_QUEUE
from schemas import (
    DBricksModel,
    DBricksModelResponse,
    DBricksRun,
    DBricksRunResponse,
    RunFeedBack,
    RunFeedBackResponse,
    MODELS_COLLECTION,
    RUNS_COLLECTION,
    FEEDBACK_COLLECTION,
)


async def get_model_list(skip: int = 0, limit: int = 10):
    """Returns list of models"""
    models = mongodb.mydb[MODELS_COLLECTION]
    model_list = models.find({}).sort('name', pymongo.DESCENDING
                                      ).skip(skip).limit(limit)
    model_list = list(model_list)
    convert_id_field_collection(model_list)
    # format_parameters(model_list)
    return model_list


async def save_model(model: DBricksModel):
    """Create new model"""

    # Validate data
    model.format_data()
    if not model.validate_parameters():  # TODO: Validate conn_str and container_name too
        raise exceptions.BadParamsException(
            "Files parameters must have a 'conn_str' and 'container_name'"
        )

    try:
        # Create DataBricks job for notebook
        job_id = await create_job(model)
        model.job_id = job_id
    except HTTPError as err:
        if err.response.status_code == 403:
            raise exceptions.NoAccessException("Invalid Token")

    if model.parameters:
        model.parameters = list(map(lambda param: dict(param), model.parameters))

    model = dict(model)
    models = mongodb.mydb[MODELS_COLLECTION]

    # Save model
    models.insert_one(model)
    convert_id_field_collection([model])
    model = parse_obj_as(List[DBricksModelResponse], [model])[0]

    return model


async def update_model(model: DBricksModelResponse):
    """Edit model with news values"""

    # Validate data
    model.format_data()
    if not model.validate_parameters():  # TODO: Validate conn_str and container_name too
        raise exceptions.BadParamsException(
            "Files parameters must have a 'conn_str' and 'container_name'"
        )

    # Get model to edit it
    models = mongodb.mydb[MODELS_COLLECTION]
    model_db = models.find_one({"_id": ObjectId(model.id)})

    try:  # TODO: check different use cases
        if model_db['workspace'] == model.workspace:
            # if is same workspace we can edit the DataBricks Job
            await update_job(model)
        else:
            # if is not same workspace we must delete old Job and create a new
            await delete_job(model)
    except HTTPError as err:
        if err.response.status_code == 403:
            raise exceptions.NoAccessException("Invalid Token")
    except Exception as ex:
        pass

    # TODO: Esto deberia estar despues de delete_job(). wtf?
    model.job_id = await create_job(model)

    if model.parameters:
        model.parameters = list(map(lambda param: dict(param), model.parameters))

    models.update_one({'_id': ObjectId(model.id)},
                      {'$set': {
                        'name': model.name,
                        'workspace': model.workspace,
                        'notebook_name': model.notebook_name,
                        'cluster_name': model.cluster_name,
                        'token': model.token,
                        'parameters': model.parameters,
                        'output_path': model.output_path,
                        'job_id': model.job_id
                      }})
    return model


async def delete_model(modelUID: str):
    """Delete DataBricks job and model from db"""
    models = mongodb.mydb[MODELS_COLLECTION]

    model = models.find_one({'_id': ObjectId(modelUID)})

    model = parse_obj_as(List[DBricksModelResponse], [model])[0]
    try:
        # Drop DataBricks job
        await delete_job(model)
    except Exception as ex:
        pass

    models.delete_one({'_id': ObjectId(modelUID)})

    return model


async def save_run(run: DBricksRun):
    """Insert a new run in Queue to be executed"""
    if run.parameters:
        run.parameters = list(map(lambda param: dict(param), run.parameters))
    run = dict(run)

    runs = mongodb.mydb[RUNS_COLLECTION]

    run["model_id"] = ObjectId(run["model_id"])
    runs.insert_one(run)
    convert_id_field_collection([run])
    run = parse_obj_as(List[DBricksRunResponse], [run])[0]

    # put new run to be processed by Thread-Worker
    JOB_QUEUE.put(run)
    return run


async def save_feedback(feedback: RunFeedBack):
    """ Attach feedback to run"""
    feedbacks = mongodb.mydb[FEEDBACK_COLLECTION]

    feedback = dict(feedback)

    feedback["run_id"] = ObjectId(feedback["run_id"])
    feedbacks.insert_one(feedback)

    convert_id_field_collection([feedback])
    feedback = parse_obj_as(List[RunFeedBackResponse], [feedback])[0]
    return feedback


async def get_feedback(run_uid):
    """ Return a list of feedback by a run"""
    feedbacks = mongodb.mydb[FEEDBACK_COLLECTION]

    feedback_list = list(feedbacks.find({'run_id': ObjectId(run_uid)}))

    convert_id_field_collection(feedback_list)
    feedback_list = parse_obj_as(List[RunFeedBackResponse], feedback_list)
    return feedback_list


async def get_runs_list(model_uid, skip: int = 0, limit: int = 10):
    """Return list of runs from a model"""
    runs = mongodb.mydb[RUNS_COLLECTION]
    runs = runs.find({"model_id": ObjectId(model_uid)}).sort('date', pymongo.DESCENDING
                                                             ).skip(skip).limit(limit)
    runs = list(runs)
    convert_id_field_collection(runs, ["model_id"])
    return runs


async def get_params_storage_sas(model_uid):
    """Get token sas to upload file from FrontEnd"""
    models = mongodb.mydb[MODELS_COLLECTION]
    model = models.find_one({"_id": ObjectId(model_uid)})
    return get_param_sas(model)


async def export_results(model_uid, run_uid, dbricks_run_id,):
    """Download run form databricks"""
    models = mongodb.mydb[MODELS_COLLECTION]
    model = models.find_one({"_id": ObjectId(model_uid)})

    params = {"run_id": dbricks_run_id,
              "views_to_export": "CODE" if model['output_path'] == "notebook" else "DASHBOARDS"}

    runs = mongodb.mydb[RUNS_COLLECTION]
    run = runs.find_one({"_id": ObjectId(run_uid)})

    name_view = model['output_path'] if run['status'] == "done" else "notebook"

    try:
        logger.info("Start exporting")
        tmp_file = await export_job_results(model, params)
        tmp_path = utils.extract_content(tmp_file, name_view)
    except Exception as ex:
        traceback.print_exc()
        logger.debug(ex)
        raise exceptions.NotExportException("Can't export dashboard. Content is too long.")

    logger.info("Finish exporting")
    return tmp_path


def remove_tmpfile(tmp_path):
    os.unlink(tmp_path)
