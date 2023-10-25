import os
from copy import copy
import pymongo


class MongoDBClass:
    myclient = ""
    mydb = ""

    def __init__(self):
        self.myclient = pymongo.MongoClient(os.getenv("MONGO_SERVER"))
        self.mydb = self.myclient[os.getenv("DATABASE_NAME")]
        self.mydb.authenticate(os.getenv("MONGO_USER"), os.getenv("MONGO_PWD"))


def convert_id_field_collection(documents, fields=None):
    for d in documents:
        convert_id_field_single(d, fields)


def convert_id_field_single(document, fields=None):
    if fields:
        for field in fields:
            document[field] = str(document[field])
    document["id"] = str(document["_id"])
    del document["_id"]


def format_parameters(documents):
    for document in documents:
        parameters = []
        for param in document["parameters"]:
            format_params = {}
            for key in param.keys():
                if param[key]:
                    format_params[key] = param[key]
            parameters.append(format_params)
        document["parameters"] = copy(parameters)


# myclient = pymongo.MongoClient("127.0.0.1:27017")
# mydb = myclient["ml-platform"]
# mydb.authenticate("ds", "1234")
