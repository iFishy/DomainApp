
from __future__ import print_function
import httplib2
import os
import sys

from EmailTree import *

from DomainApp import *
from tkinter import *
from tkinter.ttk import *

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
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
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
         'gen_hierarchy.json')

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

emails = []

def EmailCallback(request_id, response, exception):
   if exception is not None:
      print('Exception caught in email callback funtion AnalyzeEmail', exception)
      # print('Recommended to implement exponential backoff')
      sys.exit
   else:
      emails.append(Email(response))
   return

def getEmails(service, messageIDs):
   user_id = 'me'
   # div = 500

   try:
      count = 0
      batchSize = 100

      for msg in messageIDs:
         if count == 0:
            batch = service.new_batch_http_request(callback=EmailCallback)
         batch.add(service.users().messages().get(userId=user_id, id=msg['id']))
         count += 1
         if count == batchSize:
            # sys.stdout.write("[%%%5.2f]" % (len(emails) / len(messageIDs)*100))
            batch.execute()
            sys.stdout.write('\r%d / %d [%%%5.2f]' % (len(emails), len(messageIDs), (len(emails) / len(messageIDs)*100)))
            count = 0
      if count > 0:
         batch.execute()
         sys.stdout.write('\r%d / %d' % (len(emails), len(messageIDs)))
   except errors.HttpError as error:
      print('An error occurred: %s' % error)

   print()
   return

def ListAllMessageIDs(service):

   query = ''
   user_id = 'me'

   try:
      response = service.users().messages().list(userId=user_id, q=query).execute()
      messages = []
      if 'messages' in response:
         messages.extend(response['messages'])
      while 'nextPageToken' in response:
         page_token = response['nextPageToken']
         response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
         messages.extend(response['messages'])
   except errors.HttpError as error:
      print('An HTTP error occurred: %s' % error)
   return messages

def PrintHierarchy(base):
   stack = []
   depthStack = []
   stack.append(base)
   depthStack.append(-1)

   while (len(stack) != 0):
      curNode = stack.pop()
      curDepth = depthStack.pop()
      # if (curNode.__class__.__name__ == 'TreeNode'):
      if isinstance(curNode, DomainNode):
         for _ in range(curDepth):
            print('   ', end='')
         # if '@' in curNode.value:
         print(curNode.prefix, curNode.value, end = '')
         print(' (%d)' % len(curNode.childNodes))
         for child in reversed(sorted(curNode.childNodes)):
            stack.append(curNode.childNodes[child])
            depthStack.append(curDepth + 1)
         for address in reversed(sorted(curNode.addresses)):
            print(address)

def SavePickle(filename, toPickle):
   try:
      print('Pickling \'%s\'' % filename)
      with open(filename, 'wb') as fp:
         pickle.dump(toPickle, fp)
   except Exception as e:
      print('Error occurred while pickling \'%s\':' % filename, e)
   except Exception as e:
      print('Unknown error while pickling \'%s\':' % filename, e)
      print('Exiting...')
      sys.exit

def main():
   credentials = get_credentials()
   http = credentials.authorize(httplib2.Http())
   service = discovery.build('gmail', 'v1', http=http)

   # look for messageIDs pickle and load if it exists
   messageIDs = {}
   try:
      print('Looking for \'messageIDs\' pickle')
      messageIDs = pickle.load( open('messageIDs', 'rb'))
   except FileNotFoundError as e:
      print("Pickle \'messageIDs\' not found, loading from server:", e)
      messageIDs = ListAllMessageIDs(service)
      SavePickle('messageIDs', messageIDs)

   print('Total messageIDs: ', len(messageIDs))

   # look for emails pickle and load if it exists
   global emails
   try:
      print('Looking for \'emails\' pickle')
      emails = pickle.load(open('emails', 'rb'))
   except FileNotFoundError as e:
      print('Pickle \'emails\' not found, loading emails from server:')
      getEmails(service, messageIDs)
      SavePickle('emails', emails)

   print('Total emails:', len(emails))

   # generate hierarchy
   base = DomainNode('base', '')
   count = 0
   for email in emails:
      curNode = base
      for domain in reversed(email.domains):
         # add a domain node if it doesn't already exist
         if domain not in curNode.childNodes.keys():
            if curNode != base:
               curNode.childNodes[domain] = DomainNode(domain, curNode.prefix + '.' + curNode.value)
            else:
               curNode.childNodes[domain] = DomainNode(domain, '')
            
         # go down to next node
         curNode = curNode.childNodes[domain]

      # should be at end where we want to add address
      # add address in at curNode if it doesn't exist
      if email.address not in curNode.addresses.keys():
         curNode.addresses[email.address] = Address(email.address)
      # add email to address object
      curNode.addresses[email.address].emails.append(email)

   PrintHierarchy(base)

   # save hierarchy
   SavePickle('hierarchy', base)

   tk.mainloop()


if __name__ == '__main__':
   main()

