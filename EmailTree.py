"""
Email holds domain information and email data
the domains list should really be held by the DomainNode though
may change this to hold messageID instead of data
"""
class Email:
   def __init__(self, data):
      self.data = data
      self.domains = None
      self.address = None
      # Parse out domains
      for header in data['payload']['headers']:
         if 'From' == header['name']:
            self.address = header['value']
            self.address = self.address.split('>')[0].split('<')[-1]
            temp = self.address.split('@')
            assert len(temp) == 2
            self.domains = temp[1].lower().split('.')
            break
      assert self.domains is not None
      assert self.address is not None


"""
Domain node contains a string for the domain part it represents,
children nodes and a list of addresses under that domain
"""
class DomainNode:
   def __init__(self, value, prefix):
      self.prefix = prefix
      self.value = value
      self.childNodes = {}
      self.addresses = {}
      self.tags = {}

"""
Address holds an address string 
and all emails sent by that address
"""
class Address:
   def __init__(self, value):
      self.value = value
      self.emails = []
      self.tags = []

