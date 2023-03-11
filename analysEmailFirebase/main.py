# Import necessary modules and functions
from __future__ import print_function
from firebase import *
from gmailApi import *
from google.api_core.exceptions import TooManyRequests
import time

# Define a function to check for updates in Firebase Inbox


def check_firebase_inbox_update(db):
    # Get a reference to the 'user' collection in the database
    users_ref_parent = db.collection('user')
    # Get a stream of all documents in the 'user' collection
    users = users_ref_parent.stream()
    # Loop through all the documents in the parent collection
    try:
        for user in users:
            # Get the value of the 'mailboxId' field for this user
            mailbox_id = user.to_dict().get('mailboxId')
            # Check if the 'mailboxId' field exists
            if mailbox_id:
                # Check if the 'isMailboxServiceOn' field is set to True, meaning User has an active service
                if user.get('isMailboxServiceOn') == True:
                    # Get the value of the 'lastMsgInboxDate' field for this user
                    lastMsgInboxDate = user.to_dict().get('lastMsgInboxDate')
                    print("lastMsgInboxDate: ", lastMsgInboxDate)
                    # Fetch the unread emails for the user from Gmail API
                    read_email_list = read_emails_DB(db, user)
                    # Get the date of the latest unread email for the user from Gmail API
                    lastMsgInboxDateGmail = get_last_date(read_email_list)

                    print("lastMsgInboxDateGmail: ", lastMsgInboxDateGmail)
                    # Check if the latest unread email date is different from the lastMsgInboxDate stored in Firebase
                    if not lastMsgInboxDateGmail == lastMsgInboxDate:
                        # Save the unread emails to Firebase
                        save_emails_to_Firebase(
                            db, user, read_email_list, lastMsgInboxDate)
                        # Update lastMsgInboxDate in Firebase with the date of the latest unread email
                        user.reference.update(
                            {'lastMsgInboxDate': lastMsgInboxDateGmail})
                        print("-------------messages were saved------------------")
    except Exception as error:
        # Catch any exceptions that occur and print an error message
        print(f'An error occurred: {error}')
        pass

# Define the main function


def main():
    # Initialize Firebase
    db = init_firebase()
    # Start an infinite loop to check for updates in Firebase Inbox every 60 seconds
    while True:
        check_firebase_inbox_update(db)
        time.sleep(60*1)  # Minutes


# Run the main function if this file is being executed directly
if __name__ == '__main__':
    main()
