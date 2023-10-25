from fastapi import HTTPException


class ClusterNotFoundException(HTTPException):
    def __init__(self, message=None, status_code=400):
        super().__init__(status_code=status_code, detail=message)


class RunFailedException(HTTPException):
    def __init__(self, message=None, status_code=400):
        super().__init__(status_code=status_code, detail=message)


class NoAccessException(HTTPException):
    def __init__(self, message=None, status_code=403):
        super().__init__(status_code=status_code, detail=message)


class NotExportException(HTTPException):
    def __init__(self, message=None, status_code=400):
        super().__init__(status_code=status_code, detail=message)


class BadParamsException(HTTPException):
    def __init__(self, message=None, status_code=413):
        super().__init__(status_code=status_code, detail=message)
