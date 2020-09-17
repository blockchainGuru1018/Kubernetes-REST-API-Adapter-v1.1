from django.utils import timezone
from datetime import datetime, timedelta
import re
import requests

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.utils import json
