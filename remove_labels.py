from __future__ import print_function
import httplib2
import os
import sys

import pickle

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
   import argparse
   flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
   flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.labels'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Inbox Organize'

def get_credentials():
   """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
   home_dir = os.path.expanduser('~')
   credential_dir = os.path.join(home_dir, '.credentials')
   if not os.path.exists(credential_dir):
      os.makedirs(credential_dir)
   credential_path = os.path.join(credential_dir,
         'gmail-python-quickstart.json')

   store = Storage(credential_path)
   credentials = store.get()
   if not credentials or credentials.invalid:
      flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
      flow.user_agent = APPLICATION_NAME
      if flags:
         credentials = tools.run_flow(flow, store, flags)
      else: # Needed only for compatibility with Python 2.6
         credentials = tools.run(flow, store)
      print('Storing credentials to ' + credential_path)
   return credentials

def GetLabels(service, user_id):
   try:
      response = service.users().labels().list(userId=user_id).execute()
      labels = response['labels']
      """
      for label in labels:
         print ('Label id: %s - Label name: %s' % (label['id'], label['name']))
      """
      return labels
   except errors.HttpError as error:
      print ('An error occurred: %s' % error)

def DeleteLabel(service, user_id, label_id):
   try:
      service.users().labels().delete(userId=user_id, id=label_id).execute()
      print ('Label with id: %s deleted successfully.' % label_id)
   except errors.HttpError as error:
      print ('An error occurred: %s' % error)

def main():
   credentials = get_credentials()
   http = credentials.authorize(httplib2.Http())
   service = discovery.build('gmail', 'v1', http=http)

   userId = 'me'

   labels = GetLabels(service, userId)

   for label in labels:
      if (label['type'] == 'user'):
         print('Deleting label:', label['name'])
         DeleteLabel(service, userId, label['id'])

if __name__ == '__main__':
   main()

