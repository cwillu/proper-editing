import gedit
import cPickle as pickle
import os
from pprint import pformat

class SessionStateSaver(gedit.Plugin):
  def __init__(self):
    gedit.Plugin.__init__(self)

    self.app = gedit.app_get_default()
    self.callbacks = {}

    self.activated = False
    self.loaded = False
    
#    self.restoreState(self.loadState())
#    self.loading = False
    
    #restoredWindow = gedit.App().create_window()
    
#    restoredWindow.create_tab_from_uri(uri, encoding=None, line_pos=1, create=False, jump_to=False) 
  def realInit(self, window):
    self.activated = True
    self.restoreState(window, self.loadState())
    self.loaded = True
    
    
  def activate(self, window):
    if not self.activated:
      self.realInit(window)
  
    def store(*args):
      if self.loaded:
        self.saveState(self.getState())

    callbacks = []
    self.callbacks[window] = callbacks
    for event in ['tab-added', 'tabs-reordered']:
      callbackID = window.connect(event, store)
      callbacks.append(callbackID)
      
  def deactivate(self, window):
    for callbackID in self.callbacks[window]:    
      window.disconnect(callbackID)
    del self.callbacks[window]

  def update_ui(self, window):
    pass

  def getState(self, *args):
    state = []
    for window in self.app.get_windows():
      windowURIs = []
      for doc in window.get_documents():
        uri = doc.get_uri()
        print uri
        if not uri:
          continue
        windowURIs.append(uri)
      state.append(windowURIs)
    
    return state
  
  def saveState(self, state):
    print "saving", pformat(state)
    pickle.dump(state, open(os.path.expanduser('~/.gedit_state'), 'w'))
    
  def loadState(self):
    try:
      return pickle.load(file(os.path.expanduser('~/.gedit_state')))
    except (IOError, EOFError):
      return []

  def restoreState(self, window, state):
    print "restoring", pformat(state)
    for windowList in state:
      if not window:
        window = self.app.create_window()
        window.show()
      for uri in windowList:
        window.create_tab_from_uri(uri, encoding=None, line_pos=1, create=False, jump_to=False) 
      if windowList:
        window = None

