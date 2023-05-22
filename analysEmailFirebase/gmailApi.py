# Gmail API
import os
import json
import base64
import os.path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import email.utils
import datetime
from datetime import datetime, timedelta
import json

# to clean emails
import re
from bs4 import BeautifulSoup

# to analyzed body
from email_body_analyser import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_credentials(db, user):
    """
    This function retrieves the Gmail API credentials from Firebase.
    If the token is not found in Firebase, a new token will be created and saved in Firebase.
    """
    # Reference to the users collection in Firebase
    users_ref = db.collection('user')
    # Reference to the specific user's document in Firebase
    user_ref = users_ref.document(user.id)

    # Retrieve the token stored in the user's document in Firebase
    user_token = user_ref.get().to_dict().get('token')

    if user_token is None or user_token == '':
        creds = None
        # Check if token.json exists
        if os.path.exists('token.json'):
            # If token.json exists, load credentials from it
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # If credentials are expired, refresh them
                creds.refresh(Request())
            else:
                # If there are no valid or expired credentials, create a new set of credentials
                flow = InstalledAppFlow.from_client_secrets_file(
                    'C:/Users/sebas/Desktop/Workspace/JobSearchNinja/credentials.json',
                    SCOPES)  # complete address for safe reasons
                creds = flow.run_local_server(port=0)

        # Convert credentials to JSON and save in the user's document in Firebase
        user_token = creds.to_json()
        user_ref.update({'token': user_token})
    else:
        # If the token is found in Firebase, load it and convert to credentials
        user_token = json.loads(user_token)
        creds = Credentials.from_authorized_user_info(
            info=user_token, scopes=SCOPES)

    return creds


def call_gmail_api(creds, user):
    """
    This function calls the Gmail API to retrieve the unread messages in the inbox.
    """
    print("Init call_gmail_api")

    lastMsgInboxDate = user.to_dict().get('lastMsgInboxDate')

    if lastMsgInboxDate is None or lastMsgInboxDate == "":
        read_emails_after = 'after:2023/01/01'
        num = 500
    else:
        read_emails_after = 'after:' + \
            subtract_1_day(format_date(lastMsgInboxDate))
        num = 100

    print("lastMsgInboxDate:", lastMsgInboxDate)
    print("read_emails_after: ", read_emails_after)
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        # results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        results = service.users().messages().list(userId='me', labelIds=[
            'INBOX'], maxResults=num,  q=read_emails_after).execute()
        messages = results.get('messages', [])
        total_messages = results.get('resultSizeEstimate')
        print("total_messages: ", total_messages)
        print("End call_gmail_api")
        return messages

    except HttpError as error:
        # Handle errors from the Gmail API
        print(f'An error occurred: {error}')
        return None


def read_emails_DB(db, user):
    print("read_emails_DB: ", user.id)
    count_email = 0
    # Call the function that retrieves the Gmail API credentials
    creds = get_credentials(db, user)
    # Call the function that retrieves the list of messages
    messages = call_gmail_api(creds, user)
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    # Initialize an empty list to store the data of each email
    email_data_list = []
    # Loop through each message in the list of messages
    for message in reversed(messages[-10:]):
        # Get the details of the current message
        msg = service.users().messages().get(
            userId='me', id=message['id']).execute()
        # Get the headers of the current message
        headers = msg['payload']['headers']
        # Initialize an empty dictionary to store the data of the current email
        email_data = {}
        # Loop through each header in the headers of the current message
        for values in headers:
            # Get the name of the current header
            name = values["name"]
            # If the name of the current header is "From", store the value in the "from" key of the email_data dictionary
            if name == 'From':
                from_name = values["value"]
                email_data['from'] = from_name
            # If the name of the current header is "Date", store the value in the "date" key of the email_data dictionary

            if name == 'Date':
                date = values["value"]

                email_data['date'] = date
            if name == 'Subject':
                subject = values["value"]
                email_data['subject'] = subject
        # If the current message has parts
        if 'parts' in msg['payload']:
            # Get the parts of the current message
            parts = msg['payload']['parts']
            # Loop through each part in the parts of the current message
            for part in parts:
                # If the mime type of the current part is "text/plain"
                if part['mimeType'] == 'text/plain':
                    # Get the data of the current part
                    body = part['body']['data']
                    # Decode the data of the current part
                    body = base64.urlsafe_b64decode(body.encode('UTF-8'))
                    # Convert the decoded data to a string
                    body = body.decode('utf-8')
                    #clean email body
                    body = clean_body(body)
                    # Data analysis
                    response = generate_response(messages, body)
                    # data extraction
                    company_name, job_description, email_intention = extract_info_from_string(response)
                    # Store the decoded data in the "body" key of the email_data dictionary
                    email_data['body'] = body
                    email_data['company_name'] = company_name
                    email_data['job_description'] = job_description
                    email_data['email_intention'] = email_intention

        # If the current message does not have parts
        else:
            # Get the data of the current message
            body = msg['payload']['body']['data']
            # Decode the data of the current message
            body = base64.urlsafe_b64decode(body.encode('UTF-8'))
            # Convert the decoded data to a string
            body = body.decode('utf-8')
            # clean email body
            body = clean_body(body)
            # Data analysis
            response = generate_response(messages, body)
            # data extraction
            company_name, job_description, email_intention = extract_info_from_string(response)
            # Store the decoded data in the "body" key of the email_data dictionary
            email_data['body'] = body
            email_data['company_name'] = company_name
            email_data['job_description'] = job_description
            email_data['email_intention'] = email_intention
        # Check Emails
        count_email += 1
        print("count_email: ", count_email,
              "Date: ", date, "Subject: ", subject)
        # Append the email_data dictionary to the email_data_list
        email_data_list.append(email_data)

    return email_data_list


def save_emails_to_Firebase(db, user, email_data_list, lastMsgInboxDate):
    print("save_emails_to_Firebase")
    print("Size_list: ", len(email_data_list))
    count_emails_save = 0
    print("lastMsgInboxDate: ", lastMsgInboxDate, type(lastMsgInboxDate))

    if lastMsgInboxDate == "":
        lastMsgInboxDate = "Fri, 01 Jan 2023 00:00:00 +0000"

    # format  = lastMsgInboxDate is like "Fri, 10 Feb 2023 03:25:47 +0000"
    # Get a reference to the 'user' collection in the database
    users_ref_parent = db.collection('user')
    # Get a reference to the child collection

    # Create a batch object
    batch = db.batch()

    # Get a reference to the user document
    user_ref = users_ref_parent.document(user.id)

    # Get a reference to the child collection
    user_email_ref_child = user_ref.collection("email")

    ref_date = format_date(lastMsgInboxDate)
    # Get count emails saved in Firestore
    unreadEmailCount = user.to_dict().get('unreadEmailCount')

    for email_data in email_data_list:

        date = format_date(email_data.get("date"))
        datetime = format_dateAsDatetime(email_data.get("date"))
        # Check if the date of the current email is greater than the last recorded date
        if date > ref_date:
            # Generate a new document reference and add set() operation to the batch
            email_doc_ref = user_email_ref_child.document()
            batch.set(email_doc_ref, {
                "from": email_data.get("from"),
                "subject": email_data.get("subject"),
                "date": datetime,
                "body": email_data.get("body"),
                "company_name": email_data.get("company_name"),
                "job_description": email_data.get("job_description"),
                "email_intention": email_data.get("email_intention"),

            })

            count_emails_save += 1
            print("This is the type of date:", type(datetime))
            print(count_emails_save, "Subject: ", email_data.get(
                "subject"), "date: ", email_data.get("date"))

    # Commit the batch
    batch.commit()

    user.reference.update(
        {'unreadEmailCount': count_emails_save + unreadEmailCount})


def format_date(date_str):
    # Date string format: "Fri, 10 Feb 2023 03:25:47 +0000"
    # Remove the time zone information
    date_str = date_str[:24]
    # Convert the date string to a datetime object
    date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
    # Return the formatted date string
    return date.strftime('%Y-%m-%d %H:%M:%S')


def format_dateAsDatetime(date_str):
    # Date string format: "Fri, 10 Feb 2023 03:25:47 +0000"
    # Remove the time zone information
    date_str = date_str[:24]
    # Convert the date string to a datetime object
    date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
    # Return the formatted date string
    return date


"""
Secundary fuctions
"""

def clean_body(text):
    if has_html_tags(text):
        print('The email body contains HTML content')
        soup = BeautifulSoup(text, 'html.parser')
        # extract the text content of the email body
        soup_clean = soup.get_text()
        return soup_clean
    if has_url(text):
        print("Email contains a URL")
        # Remove URLs
        urls_removed = re.sub(r'http\S+', '', text)
        return urls_removed
    else:
        print('The email body does not contain HTML content')
        print("Email does not contain a URL")
        return text


def has_url(text):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return bool(url_pattern.search(text))
def has_html_tags(text):
    """Returns True if the given text contains HTML tags, False otherwise"""
    return '<html>' in text.lower() or '<body>' in text.lower() or '<p>' in text.lower() or '</p>' in text.lower() or '</div>' in text.lower()





def get_total_messages():

    try:
        service = build('gmail', 'v1', credentials=creds)
        # Call the Gmail API to get the total number of messages in the mailbox
        response = service.users().messages().list(
            userId='me', labelIds=["INBOX"], maxResults=1).execute()
        total_messages = response.get('resultSizeEstimate', 0)
        return total_messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def subtract_1_day(date_string):
    # Convert the string to a datetime object
    date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    # Subtract 10 minutes from the datetime object
    new_date = date - timedelta(days=1)

    # Convert the datetime object back to a string in the same format as the original
    new_date_string = datetime.strftime(new_date, "%Y-%m-%d")

    return new_date_string


def count_unread_messages(messages):
    """
    This function counts the number of unread messages.
    """
    if not messages:
        print('No unread messages found.')
        return 0
    else:
        return len(messages)


def check_user_inbox_unread(db, user):
    """
    This function retrieves the number of unread messages in the Gmail inbox.
    """
    creds = get_credentials(db, user)
    messages = call_gmail_api(creds)
    unread_count = count_unread_messages(messages)
    return unread_count


def get_last_date(email_data_list):
    # Initialize a variable to store the last date
    last_date = email_data_list[-1]['date']
    return last_date
