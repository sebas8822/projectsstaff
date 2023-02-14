# Firebase
import firebase_admin
from firebase_admin import credentials  # for authentication
from firebase_admin import firestore
import imaplib
import email


def init_firebase():
    # Initialize Firebase using the given certificate file
    cred = credentials.Certificate("C:/Users/sebas/Desktop/Workspace/JobSearchNinja/package-lock.json")
    firebase_admin.initialize_app(cred)
    # Connect to the Firestore database
    db = firestore.client()
    return db


def generate_id():
    return firestore.DEFAULT_DOCUMENT_ID