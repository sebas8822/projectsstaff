from __future__ import print_function

from firebase import *
from gmailApi import *

# Schedule Task
import time


def main():
    # Initialize FireBase Function
    db = init_firebase()

    while True:
        # Fetch the data for users with mailbox service enabled
        check_firebase_inbox_update(db)
        time.sleep(600)  # wait for 10 minutes


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
            # Check if the 'isMailboxServiceOn' field is set to True means User has an active service
            if user.get('isMailboxServiceOn') == True:
                lastMsgInboxDate = user.to_dict().get('lastMsgInboxDate')
                # print("lastMsgInboxDate: ", lastMsgInboxDate, "type: ", type(lastMsgInboxDate))
                lastMsgInboxDateGmail = get_last_date(read_emails_DB(db, user))
                # print("Last Date unread message from User Gmail: ", lastMsgInboxDateGmail, "lastMsgInboxDateGmail", type(lastMsgInboxDateGmail))
                # print(lastMsgInboxDateGmail==lastMsgInboxDate)

                if not lastMsgInboxDateGmail == lastMsgInboxDate:
                    # Read the emails and save them into firebase
                    save_emails_to_Firebase(db, user, read_emails_DB(db, user), lastMsgInboxDate)
                    # Update unreadEmailCount in firebase with current current_user_unread_msg value
                    user.reference.update({'lastMsgInboxDate': lastMsgInboxDateGmail})


if __name__ == '__main__':
    main()
