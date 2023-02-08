
from __future__ import print_function

# Firebase
import firebase_admin
from firebase_admin import credentials # for authentication
from firebase_admin import firestore
import imaplib
import email

#Gmail API
import os.path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    # Initialize FireBase Function
    db = init_firebase()
    # Fetch the data for users with mailbox service enabled
    fetch_users_true(db)


def init_firebase():
    # Initialize Firebase using the given certificate file
    cred = credentials.Certificate("C:/Users/sebas/Desktop/Workspace/JobSearchNinja/package-lock.json")
    firebase_admin.initialize_app(cred)
    # Connect to the Firestore database
    db = firestore.client()
    return db

def fetch_users_true(db):
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
                    # If the unread email count from the database does not match the current unread message count in the user's inbox
                    # Get a reference to the 'email' collection for this user

                    read_emails_write_DB(db)

                    """
                    user_email_ref = users_ref_parent.document(user.id).collection("email")
                    # Get a stream of all documents in the 'email' collection for this user
                    user_emails = user_email_ref.stream()
                    # Loop through all the documents in the child collection
                    for email in user_emails:
                        # Print the ID and data for each email document
                        print(f"email ID: {email.id}")
                        print(f"email data: {email.to_dict()}")
                        """






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

def read_emails_write_DB(db):
    creds = get_credentials()
    messages = call_gmail_api(creds)
    service = build('gmail', 'v1', credentials=creds)



    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_data = msg['payload']['headers']
        for values in email_data:
            name = values["name"]
            if name == 'From':
                from_name = values["value"]
                print("You have a new message from: " + from_name + '\n')
                print(msg['snippet'] + "..." + '\n')

                # Add the email data to the Firestore database
                doc_ref = db.collection("emails").document()
                doc_ref.set({
                    "from": from_name,
                    "snippet": msg['snippet']
                })








if __name__ == '__main__':
    main()