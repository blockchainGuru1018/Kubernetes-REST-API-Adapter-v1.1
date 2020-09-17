from rest_framework import status
from background_task import background
from logging import getLogger
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
import requests
from rest_framework.utils import json
import time
from .models import Server
from common.serializers import server_active, server_inactive
from .views import finished_processing_spreadsheet


def spreadsheet(*args, **kwargs):
    print("[robot voice] processing spreadsheet.........")
    finished_processing_spreadsheet()
