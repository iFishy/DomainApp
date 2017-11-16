from __future__ import print_function
import httplib2
import os
import sys

from EmailTree import *

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
SCOPES = 'https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.labels'
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
         'modify_labels.json')

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

def CreateLabel(service, user_id, labelStr):
   try:
      label = service.users().labels().create(userId=user_id,
            body={'name' : labelStr}).execute()
      return label['id']
   except errors.HttpError as error:
      print ('An error occurred: %s' % error)

def AddLabelCallback(request_id, response, exception):
   if exception is not None:
      print('Failed to add label to an email:', exception)
   return

def main():
   credentials = get_credentials()
   http = credentials.authorize(httplib2.Http())
   service = discovery.build('gmail', 'v1', http=http)

   userId = 'me'

   # load hierarchy
   try:
      print('Looking for \'hierarchy\' pickle')
      base = pickle.load(open('hierarchy', 'rb'))
   except FileNotFoundError as e:
      print('Pickle \'hierarchy\' not found')
      print('Exiting...')
      sys.exit


   stack = []
   stack.append(base)

   batchSize = 10
   count = 0

   while (len(stack) != 0):
      curNode = stack.pop()

      labelStr = curNode.prefix + '.' + curNode.value
      labelStr = labelStr[1:]

      if len(curNode.addresses) != 0:
         labelId = CreateLabel(service, 'me', labelStr)
         print (labelStr)
      # go through addresses and add labelId to each email
      for address in curNode.addresses:
         for email in curNode.addresses[address].emails:
            if (count == 0):
               batch = service.new_batch_http_request(callback = AddLabelCallback)
            batch.add(service.users().messages().modify(userId='me', id=email.data['id'], body={'removeLabelIds' : [], 'addLabelIds' : [labelId]}))
            count += 1
            if count == batchSize:
               batch.execute()
               count = 0
         if count > 0:
            batch.execute()
            count = 0
      if count > 0:
         batch.execute()
      # add children to stack
      for child in reversed(sorted(curNode.childNodes)):
         stack.append(curNode.childNodes[child])

   print('done')


if __name__ == '__main__':
   main()

