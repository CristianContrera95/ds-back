import os
import re
from api import logger
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    AccountSasPermissions,
    ResourceTypes,
    generate_account_sas
)
from settings.config import (
    CLIENT_TOKEN_DURATION_IN_HOURS,
    STORAGE_CONN_STR,
    FEEDBACK_CONTAINER
)
from core.storage.exceptions import CloudCredentialsException


def storage_connect(conn_str, container_name):
    blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(
        conn_str)
    container_client: ContainerClient = blob_service_client.get_container_client(
        container_name)
    return container_client


def save_upload_file_storage(upload_file: UploadFile, conn_str, container_name, folder="") -> Path:
    container_client = storage_connect(conn_str, container_name)
    try:
        if folder:
            folder += os.sep
        pathfile = folder + os.sep + str(uuid4()) + '-' + upload_file.filename
        blob_client = container_client.get_blob_client(pathfile)
        blob_client.upload_blob(upload_file.file, blob_type="BlockBlob")
    finally:
        upload_file.file.close()
    return Path(pathfile)


def get_feedback_sas(modelIUD: str):
    creds = __parse_azure_conn_str(STORAGE_CONN_STR)

    expiration = datetime.utcnow() + timedelta(hours=CLIENT_TOKEN_DURATION_IN_HOURS)
    return {
        'AccountName': creds['AccountName'],
        'container_name': FEEDBACK_CONTAINER,
        'sas': __get_azure_temp_token(creds, expiration),
        'folder': modelIUD
    }


def get_param_sas(current_model):
    try:
        params_keys = __parse_model_params(current_model["parameters"])
    except Exception as e:
        logger.error(str(e))
        raise CloudCredentialsException("Connection string has bad format o values")

    expiration = datetime.utcnow() + timedelta(hours=CLIENT_TOKEN_DURATION_IN_HOURS)
    for param in params_keys.keys():
        params_keys[param].update({"sas": __get_azure_temp_token(params_keys[param], expiration)})
        del params_keys[param]["AccountKey"]

    return params_keys


def __get_azure_temp_token(creds, expiration):
    try:
        sas_token = generate_account_sas(
            account_name=creds["AccountName"],
            account_key=creds["AccountKey"],
            resource_types=ResourceTypes(object=True, service=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, list=True),
            expiry=expiration,
            # protocol=('https','http')
        )

        return sas_token

    except Exception as e:
        logger.error(str(e))
        raise CloudCredentialsException("Credentials AccountName or AccountKey are wrong")


def __parse_model_params(params):
    result = {}

    for param in params:
        if param["conn_str"]:
            result[param["name"]] = __parse_azure_conn_str(param["conn_str"])

            result[param["name"]].update({"container_name": param["container_name"]})
            result[param["name"]].update({"folder": param["folder"]})
    return result


def __parse_azure_conn_str(connection_str):

    def ToDict(a):
        it = iter([item for sublist in a for item in sublist])
        res_dct = dict(zip(it, it))
        return res_dct

    values = connection_str.split(";")
    return ToDict(map(lambda value: re.split('=(?!=|$)', value),
               filter(lambda value: value.startswith("Account"), values)))
