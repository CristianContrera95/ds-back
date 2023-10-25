import http
import time
from pathlib import Path
from subprocess import call
from contextlib import closing
from tempfile import NamedTemporaryFile

import requests

from .exceptions import RunFailedException, ClusterNotFoundException
from schemas import DBricksModel, DBricksRun, DBricksModelResponse
from settings.config import API_VERSION, JOB_MAX_CONCURRENT


# http patch from https://stackoverflow.com/questions/44509423/python-requests-chunkedencodingerrore-requests-iter-lines
def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except http.client.IncompleteRead as e:
            return e.partial
    return inner

http.client.HTTPResponse.read = patch_http_response_read(http.client.HTTPResponse.read)


def get_output(dbricksmodel: DBricksModel, run_id: int) -> None:
    """Check each 2 seconds if process finished"""
    while True:
        response = requests.get(
            f'{dbricksmodel.workspace}/{API_VERSION}/jobs/runs/get-output?run_id={run_id}',
            headers={'Authorization': 'Bearer %s' % dbricksmodel.token}
        )
        if response.status_code == 200:
            response = response.json()
            state = response['metadata']['state']
            if state.get('life_cycle_state', '') == "TERMINATED":
                if state.get('result_state', '') != "SUCCESS":
                    raise RunFailedException(response['notebook_output'].get('result', "failed at notebook"))
                return
        time.sleep(2)


def run_job(dbricksmodel: DBricksModel, dbricksrun: DBricksRun) -> (int, int):
    """Run now the associate job and return run_id"""
    response = requests.post(f"{dbricksmodel.workspace}/{API_VERSION}/jobs/run-now",
                             json={
                                  "job_id": dbricksmodel.job_id,
                                  "notebook_params": {
                                             param.name: param.value for param in dbricksrun.parameters
                                         }
                                },
                            headers={'Authorization': 'Bearer %s' % dbricksmodel.token})
    response.raise_for_status()
    response = response.json()
    return response.get('run_id', 0), response.get('number_in_job', 0)


async def list_clusters(dbricksmodel: DBricksModel):
    """Get list of cluster available in databricks"""
    response = requests.get(f"{dbricksmodel.workspace}/{API_VERSION}/clusters/list",
                            headers={'Authorization': 'Bearer %s' % dbricksmodel.token})
    response.raise_for_status()
    return response.json()['clusters']


async def find_clusterID(dbricksmodel: DBricksModel) -> str:
    """Get ClusterID from cluster name"""
    clusters = await list_clusters(dbricksmodel)
    for cluster in clusters:
        if cluster["cluster_name"].lower() == dbricksmodel.cluster_name:
            return cluster["cluster_id"]


async def create_job(dbricksmodel: DBricksModel) -> int:
    """Create a new Job"""
    cluster_id = await find_clusterID(dbricksmodel)
    if cluster_id is None:
        raise ClusterNotFoundException(
            f"Cluster name: {dbricksmodel.cluster_name} not found in {dbricksmodel.workspace}"
        )

    response = requests.post(f"{dbricksmodel.workspace}/{API_VERSION}/jobs/create",
                             json={
                                 "name": f"ml-platform-{dbricksmodel.name}",
                                 "notebook_task": {
                                     "notebook_path": dbricksmodel.notebook_name,
                                     "base_parameters": {
                                         param.name: param.default for param in filter(
                                             lambda param: param.default, dbricksmodel.parameters)
                                     }
                                 },
                                 "existing_cluster_id": cluster_id,
                                 "max_concurrent_runs": JOB_MAX_CONCURRENT,
                             },
                             headers={'Authorization': 'Bearer %s' % dbricksmodel.token})
    response.raise_for_status()
    return response.json()["job_id"]


async def update_job(dbricksmodel: DBricksModel) -> None:
    """Update a existent Job"""
    cluster_id = await find_clusterID(dbricksmodel)
    if cluster_id is None:
        raise ClusterNotFoundException(
            f"Cluster name: {dbricksmodel.cluster_name} not found in {dbricksmodel.workspace}"
        )

    response = requests.post(f"{dbricksmodel.workspace}/{API_VERSION}/jobs/update",
                             json={
                                 "job_id": dbricksmodel.job_id,
                                 "new_settings": {
                                     "name": f"ml-platform-{dbricksmodel.name}",
                                     "notebook_task": {
                                         "notebook_path": dbricksmodel.notebook_name,
                                         "base_parameters": {
                                             param.name: param.default for param in filter(
                                                 lambda param: param.default, dbricksmodel.parameters)
                                         }
                                     },
                                     "existing_cluster_id": cluster_id,
                                     "max_concurrent_runs": JOB_MAX_CONCURRENT,
                                 }
                             },
                             headers={'Authorization': 'Bearer %s' % dbricksmodel.token})
    response.raise_for_status()


async def delete_job(dbricksmodel: DBricksModelResponse):
    """Drop job"""
    response = requests.post(f"{dbricksmodel.workspace}/{API_VERSION}/jobs/delete",
                             json={"job_id": dbricksmodel.job_id},
                             headers={'Authorization': 'Bearer %s' % dbricksmodel.token})
    response.raise_for_status()


async def export_job_results(dbricksmodel, params=None) -> Path:
    """Download results from run in a job"""
    with NamedTemporaryFile(mode='wb', delete=False, suffix=".html") as tmp:
        tmp_file = Path(tmp.name)
        call([
            "curl",
            f'{dbricksmodel["workspace"]}/{API_VERSION}/jobs/runs/export?'
                f'run_id={params["run_id"]}&views_to_export={params["views_to_export"]}',
            '-H', 'Connection: keep-alive',
            '-H', 'Cache-Control: max-age=0',
            '-H', 'Upgrade-Insecure-Requests: 1',
            '-H',
            'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            '-H', 'Sec-Fetch-Mode: navigate',
            '-H',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            '-H', 'Sec-Fetch-Site: cross-site',
            '-H', 'Accept-Encoding: gzip, deflate, br',
            '-H', 'Accept-Language: en-US,en;q=0.9,bn;q=0.8',
            '-H', f'Authorization: Bearer {dbricksmodel["token"]}',
            '--compressed', '--output', tmp_file
        ])

    return tmp_file

    # with closing(requests.get(f"{dbricksmodel['workspace']}/{API_VERSION}/jobs/runs/export",
    #                         params=params,
    #                         headers={'Authorization': 'Bearer %s' % dbricksmodel['token']},
    #                         stream=True)) as response:
    #
    #     response.raise_for_status()
    #
    #     with NamedTemporaryFile(mode='wb', delete=False, suffix=".html") as tmp:
    #         # shutil.copyfileobj(response.raw, tmp)
    #         for chunk in response.iter_content(chunk_size=1024*16):
    #             tmp.write(chunk)
    #
    #     return tmp_file
