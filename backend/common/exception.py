from rest_framework.exceptions import PermissionDenied
from rest_framework import status


class CustomException(PermissionDenied):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = {
        "result": False,
        "errorCode": 0,
        "errorMsg": "Internal Server Error"
    }

    def __init__(self, code, message, status_code=None):
        self.detail = {
            "result": False,
            "errorCode": code,
            "errorMsg": message
        }
        if status_code is not None:
            self.status_code = status_code
