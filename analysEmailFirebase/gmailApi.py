# Gmail API
import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email.utils
import datetime
from datetime import datetime
import json

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
    # print("User ID: ", user.id, "Customer Token: ",user_token)

    if user_token is None:
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
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        # Convert credentials to JSON and save in the user's document in Firebase
        user_token = creds.to_json()
        user_ref.set({'token': user_token})
    else:
        # If the token is found in Firebase, load it and convert to credentials
        user_token = json.loads(user_token)
        creds = Credentials.from_authorized_user_info(info=user_token, scopes=SCOPES)

    return creds


def call_gmail_api(creds):
    """
    This function calls the Gmail API to retrieve the unread messages in the inbox.
    """
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        # Handle errors from the Gmail API
        print(f'An error occurred: {error}')
        return None


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
    last_date = email_data_list[0]['date']
    return last_date


def read_emails_DB(db, user):
    # Call the function that retrieves the Gmail API credentials
    creds = get_credentials(db, user)
    # Call the function that retrieves the list of messages
    messages = call_gmail_api(creds)
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    # Initialize an empty list to store the data of each email
    email_data_list = []
    # Loop through each message in the list of messages
    for message in messages:
        # Get the details of the current message
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
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
                    # Store the decoded data in the "body" key of the email_data dictionary
                    email_data['body'] = body
        # If the current message does not have parts
        else:
            # Get the data of the current message
            body = msg['payload']['body']['data']
            # Decode the data of the current message
            body = base64.urlsafe_b64decode(body.encode('UTF-8'))
            # Convert the decoded data to a string
            body = body.decode('utf-8')
            # Store the decoded data in the "body" key of the email_data dictionary
            email_data['body'] = body
        # Append the email_data dictionary to the email_data_list
        email_data_list.append(email_data)
    # Print the email_data_list
    print(email_data_list)
    # Return email_data_list
    return email_data_list


def save_emails_to_Firebase(db, user, email_data_list, lastMsgInboxDate):
    print("lastMsgInboxDate: ", lastMsgInboxDate, type(lastMsgInboxDate))

    if lastMsgInboxDate == "":
        lastMsgInboxDate = "Fri, 01 Jan 2023 00:00:00 +0000"

    # format  = lastMsgInboxDate is like "Fri, 10 Feb 2023 03:25:47 +0000"
    # Get a reference to the 'user' collection in the database
    users_ref_parent = db.collection('user')
    # Get a reference to the child collection
    ref_date = format_date(lastMsgInboxDate)

    user_email_ref_child = users_ref_parent.document(user.id).collection("email")
    for email_data in email_data_list:
        date = format_date(email_data.get("date"))
        # Check if the date of the current email is greater than the last recorded date
        if date > ref_date:
            # Add a document to the child collection
            user_email_ref_child.add({
                "from": email_data.get("from"),
                "date": email_data.get("date"),
                "body": email_data.get("body")
            })


def format_date(date_str):
    # Date string format: "Fri, 10 Feb 2023 03:25:47 +0000"
    # Remove the time zone information
    date_str = date_str[:24]
    # Convert the date string to a datetime object
    date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
    # Return the formatted date string
    return date.strftime('%Y-%m-%d %H:%M:%S')
