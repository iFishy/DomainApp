import pickle

from tkinter import *
from tkinter.ttk import *
from DomainApp import DomainApp
from EmailTree import *

def main():
   root = Tk()
   tree = DomainApp(master = root).tree

   # load pickle
   try:
      print('Looking for \'hierarchy\' pickle')
      hierarchy = pickle.load(open('hierarchy', 'rb'))
   except FileNotFoundError as e:
      print('Pickle \'hierarchy\' not found')

   stack = []
   stack.append(hierarchy)

   while (len(stack) != 0):
      curNode = stack.pop()
      if (curNode != hierarchy):
         tree.insert(curNode.prefix, 0, curNode.prefix + '.' + curNode.value, \
               text = curNode.value, values = [len(curNode.childNodes)])
      if isinstance(curNode, DomainNode):
         for child in sorted(curNode.childNodes):
            stack.append(curNode.childNodes[child])
         if (len(curNode.addresses) != 0):
            for address in reversed(sorted(curNode.addresses)):
               tree.insert(curNode.prefix + '.' + curNode.value, \
                     0, address, \
                     text = address, \
                     values = [len(curNode.addresses[address].emails)])



   root.mainloop()
   root.destroy()

if __name__ == '__main__':
   main()
