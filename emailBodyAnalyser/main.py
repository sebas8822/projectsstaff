import os
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import nltk
from nltk.tokenize import sent_tokenize
import spacy
from transformers import pipeline