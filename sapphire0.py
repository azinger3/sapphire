# pylint: disable=no-member
# pylint: disable=anomalous-backslash-in-string

"""
PURPOSE:		Budget Transaction Bot - Sapphire
AUTHOR:			Rob Azinger
DATE:			03/06/2020
NOTES:
CHANGE CONTROL:
"""
from __future__ import print_function
import pickle
import os.path
import base64
import re
from datetime import datetime, timedelta
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BUDGET_API = "http://localhost:8081/budget/transaction/queue"


def go():
    """
    Budget Transaction Bot - Sapphire
    """
    print('greetings! from an imported module!!!')
