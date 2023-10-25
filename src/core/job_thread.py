from queue import Queue
from threading import Thread, get_ident as threading_get_ident
import traceback
import asyncio
from typing import List

from requests.exceptions import HTTPError
from pydantic import parse_obj_as
from bson import ObjectId

from api import logger
from schemas import (
    RunStatusEnum,
    DBricksRunResponse,
    DBricksModel,
    MODELS_COLLECTION,
    RUNS_COLLECTION
)
from core.databricks import exceptions
from core.databricks.api import run_job, get_output
from db.mongo import convert_id_field_collection


JOB_QUEUE = Queue()


class JobMaster(Thread):
    """Orchestra the queue of runs, and create Workers to process runs"""
    def __init__(self, queue: "Queue[DBricksRunResponse]", mongodb):
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.mongodb = mongodb

    async def grab_jobs_from_db(self):
        """Get jobs that started but without results yet, and put them to queue to wait results"""
        logger.info("Search 'old' pending jobs")

        modelruns = self.mongodb[RUNS_COLLECTION]
        pending_runs = list(modelruns.find({"status": {"$in": [RunStatusEnum.new,
                                                               RunStatusEnum.in_progress]}}))
        convert_id_field_collection(pending_runs)
        pending_runs = parse_obj_as(List[DBricksRunResponse], pending_runs)
        logger.info(f"Adding {len(pending_runs)} old job to Queue")
        for run in pending_runs:
            self.queue.put(run)

    def run(self):
        logger.info("Start processing queue")
        while True:
            run = self.queue.get()
            # Create a new thread to process this run
            JobWorker(run, self.mongodb).start()
            # self.queue.task_done()


class JobWorker(Thread):
    """Process a run, and wait run finish"""
    def __init__(self, job_run: DBricksRunResponse, mongodb):
        Thread.__init__(self, daemon=True)
        self.job_run = job_run
        self.mongodb = mongodb

    def run(self) -> None:
        """Run a model and wait it finish"""
        logger.info(f"Run model {self.job_run.model_id} on Thread {threading_get_ident()}")
        try:
            models = self.mongodb[MODELS_COLLECTION]
            model = models.find_one({"_id": ObjectId(self.job_run.model_id)})

            if model is None:
                raise ValueError("model is none")

            if self.job_run.status == RunStatusEnum.new:
                # if is not process already, set status to running and start running
                asyncio.run(self.job_run.update_status(self.mongodb, RunStatusEnum.in_progress))
                run_id, number_in_job = run_job(DBricksModel(**model), self.job_run)
                asyncio.run(self.job_run.set_run_id(self.mongodb, run_id, number_in_job))

            # Get results, blocking call waiting for it to end
            get_output(DBricksModel(**model), self.job_run.run_id)

            status = RunStatusEnum.done
        except HTTPError as err:
            status = RunStatusEnum.error
            msg_err = str(err)
            if err.response.status_code == 403:
                msg_err = "Invalid Token"
            if err.response.status_code == 400:
                msg_err = "Job don't exist"
            logger.error(msg_err)
        except Exception as ex:
            msg_err = str(ex)
            status = RunStatusEnum.error
            traceback.print_exc()

        # Update status and close thread
        asyncio.run(self.job_run.update_status(self.mongodb, status))
        logger.info(f"Finish model {self.job_run.model_id} on Thread {threading_get_ident()}"
                    f"with status {status}")
        if status == RunStatusEnum.error:
            raise exceptions.NoAccessException(msg_err)
