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
    # Authenticate
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Set Date Range
    start_datetime = datetime.today() - timedelta(days=2)
    end_datetime = datetime.today() + timedelta(days=2)

    start_date = start_datetime.strftime("%Y/%m/%d")
    end_date = end_datetime.strftime("%Y/%m/%d")

    # Set Query
    user_id = 'me'
    full = 'full'
    query = 'after:' + start_date + ' before:' + end_date + ' subject:Your Single Transaction Alert from Chase'

    print('Query')
    print(query)

    # List Messages (All Pages)
    response = service.users().messages().list(userId=user_id, q=query).execute()

    messages_all_pages = []

    if 'messages' in response:
        messages_all_pages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages_all_pages.extend(response['messages'])

    messages = messages_all_pages

    # Find Transactions in Message List
    if not messages:
        print('No messages found.')
    else:
        for message in messages:
            queue_id = message['id']

            # Get Message
            this_message = service.users().messages().get(userId=user_id, id=queue_id, format=full).execute()

            # Set Message
            message_body = this_message['payload']['body']['data']
            message_html = base64.urlsafe_b64decode(message_body)
            message_text = message_html.decode('utf-8').replace('($USD) ', '')

            # Set Transaction Date
            date_message = int(this_message['internalDate'])
            date_object = (date_message / 1000)
            transaction_date = datetime.fromtimestamp(date_object).strftime("%Y-%m-%d")

            # Set Amount
            amount = re.search('A charge of (.+?) at', message_text).group(1)

            # Set Description
            description = re.search('at (.+?) has', message_text).group(1)

            # Build Transaction
            transaction = {
                'QueueID': queue_id,
                'TransactionTypeID': 2,
                'TransactionDT': transaction_date,
                'Description': description,
                'Amount': amount,
                'BudgetCategoryID': '103',
                'TransactionNumber': '',
                'Note': 'CC'
            }

            print('Transaction Found')
            print(transaction)

            # Send to Queue
            response_data = requests.post(url=BUDGET_API, data=transaction)

            result = response_data.text

            if result == '1':
                print('****************** Transaction Queued ******************')
