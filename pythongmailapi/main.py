from __future__ import print_function
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
    """
    This function retrieves the unread messages in the Gmail inbox using the Gmail API.
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
                'C:/Users/sebas/Desktop/Workspace/JobSearchNinja/credentials.json', SCOPES) # complete address for safe reasons
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        if not messages:
            print('No unread messages found.')
        else:
            # Number of unread messages
            print('Number of unread messages: ', len(messages))
            read_msg_choice = input('Would you like to see the messages? (y/n) -->').lower()
            if read_msg_choice == 'y':
                # Loop through the list of messages and retrieve the message details
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = msg['payload']['headers']
                    for values in email_data:
                        name = values["name"]
                        if name == 'From':
                            from_name = values["value"]
                            print("You have a new message from: " + from_name +'\n')
                            print(msg['snippet']+"..."+'\n')
                            time.sleep(1)
            else:
                print("End application - goodbye!")
    except HttpError as error:
        # Handle errors from the Gmail API
        print(f'An error occurred: {error}')




main()