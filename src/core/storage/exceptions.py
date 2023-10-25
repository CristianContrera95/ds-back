class CloudServiceException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class CloudCredentialsException(CloudServiceException):
    def __init__(self, message):
        super().__init__(message)
