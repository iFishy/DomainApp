from tkinter import *
from tkinter.ttk import *

class DomainTree(Treeview):

   def __init__(self, master = None):
      super().__init__()

   def populateTree():
      pass

class DomainApp(Frame):

   def __init__(self, master=None):
      super().__init__()
      self.pack()

      self.tree = DomainTree(master = self)
      self.tree['columns'] = ('count')
      self.tree.pack(fill = 'both', expand = True)


if __name__ == '__main__':
   root = Tk()
   app = DomainApp(master = root)
   root.mainloop()
   root.destroy()
