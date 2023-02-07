

import firebase_admin
from firebase_admin import credentials # for authentication
from firebase_admin import firestore
import imaplib
import email

def main():
    # initialize firebase
    cred = credentials.Certificate("C:/Users/sebas/Desktop/Workspace/JobSearchNinja/package-lock.json")
    firebase_admin.initialize_app(cred)
    # reading from database

    db = firestore.client()
    fetch_users(db)

def fetch_users(db):
    users_ref = db.collection('user').stream()

    for user in users_ref:
        client = user.to_dict()
        print(user)
        if client.get('isMailboxServiceOn') == True:
            # compare current unread mailbox count against to firebase count
            # get the mailboxId and go through to remain emails
            # if current emails check the most recent to the last one checked



            print("check EmailBOX")
        else:
            print("no active users found!")

        #print("{}".format(user.to_dict()))



    #return users

def populate_users_database():
    return 1
    # populate the database with 10 users that with different information to interact to


if __name__ == '__main__':
    main()