
from __future__ import print_function

# Firebase
import firebase_admin
from firebase_admin import credentials # for authentication
from firebase_admin import firestore
import imaplib
import email

# Gmail API
import base64
import os.path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Schedule Task
import schedule



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    # Initialize FireBase Function
    db = init_firebase()
    # Fetch the data for users with mailbox service enabled
    check_firebase_inbox_update(db)


def init_firebase():
    # Initialize Firebase using the given certificate file
    cred = credentials.Certificate("C:/Users/sebas/Desktop/Workspace/JobSearchNinja/package-lock.json")
    firebase_admin.initialize_app(cred)
    # Connect to the Firestore database
    db = firestore.client()
    return db

def check_firebase_inbox_update(db):
    # Get a reference to the 'user' collection in the database
    users_ref_parent = db.collection('user')
    # Get a stream of all documents in the 'user' collection
    users = users_ref_parent.stream()
    # Loop through all the documents in the parent collection
    for user in users:
        # Get the value of the 'mailboxId' field for this user
        mailbox_id = user.to_dict().get('mailboxId')
        # Check if the 'mailboxId' field exists
        if mailbox_id:
            # Check if the 'isMailboxServiceOn' field is set to True
            if user.get('isMailboxServiceOn') == True:
                # If the 'mailboxId' field exists and 'isMailboxServiceOn' is True, retrieve the unread email count
                unreadEmailCount = user.to_dict().get('unreadEmailCount')
                print("Current messages in Database: ", unreadEmailCount)
                # Call the 'check_user_inbox_unread' function to get the current unread message count in the user's inbox
                current_user_unread_msg = check_user_inbox_unread()
                print("Current messages in User Inbox: ", current_user_unread_msg)
                # Compare the unread email count from the database with the current unread message count in the user's inbox
                if not current_user_unread_msg == unreadEmailCount:
                    # Read the emails and save them into firebase
                    save_emails_to_Firebase(db, user, read_emails_DB(db))
                    # Update unreadEmailCount in firebase with current current_user_unread_msg value
                    user.reference.update({'unreadEmailCount': current_user_unread_msg})





def get_credentials():
    """
    This function retrieves the Gmail API credentials.
    If token.json exists, the function will try to use that first to retrieve the credentials.
    If not, it will create a new token.json file by going through the authorization flow.
    """
    creds = None
    # Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/sebas/Desktop/Workspace/JobSearchNinja/credentials.json',
                SCOPES)  # complete address for safe reasons
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
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

def check_user_inbox_unread():
    """
    This function retrieves the number of unread messages in the Gmail inbox.
    """
    creds = get_credentials()
    messages = call_gmail_api(creds)
    unread_count = count_unread_messages(messages)
    return unread_count

def read_emails_DB(db):
    # Call the function that retrieves the Gmail API credentials
    creds = get_credentials()
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

def save_emails_to_Firebase(db, user, email_data_list):
    # Get a reference to the 'user' collection in the database
    users_ref_parent = db.collection('user')
    # Get a reference to the child collection
    user_email_ref_child = users_ref_parent.document(user.id).collection("email")
    for email_data in email_data_list:
        # Add a document to the child collection
        user_email_ref_child.add({
            "from": email_data.get("from"),
            "date": email_data.get("date"),
            "body": email_data.get("body")
        })






if __name__ == '__main__':
    main()