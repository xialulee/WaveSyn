from objectmodel    import ModelNode, NodeDict
from common         import Observable
import threading
import subprocess
import tempfile
import os

class EditorThread(threading.Thread):
    def __init__(self, editorPath, filename):
        self.editorPath = editorPath
        self.filename   = filename
        threading.Thread.__init__(self)

    def run(self):
        subprocess.call([self.editorPath, self.filename])

class EditorNode(ModelNode):
    def __init__(self, nodeName='', editorPath=''):
        ModelNode.__init__(self, nodeName=nodeName)
        with self.attributeLock:
            self.editorPath = editorPath
        self.__thread   = None
        self.code       = None

    def launch(self):
        if self.__thread is not None:
            raise Exception('Editor has already been launched.')
        fd, filename    = tempfile.mkstemp(suffix='.py', text=True)
        with os.fdopen(fd):
            # Close the temp file, consequently the external editor can edit it without limitations.
            pass
        with self.attributeLock:
            self.filename   = filename
        self.__thread   = EditorThread(self.editorPath, self.filename)
        self.__thread.start()

    def isAlive(self):
        alive   = self.__thread.isAlive()
        if not alive and self.code is None:
            try:
                with open(self.filename, 'r') as f:
                    self.code    = f.read()
            finally:
                os.remove(self.filename)
        return alive


class EditorManager(Observable):
    def __init__(self, editorDict):
        Observable.__init__(self)
        self.__editorDict   = editorDict

    def update(self):
        if self.__editorDict:
            for editor in self.__editorDict.itervalues():
                if not editor.isAlive():
                    self.notifyObservers(editor)
                    self.__editorDict.pop(id(editor))
                    break


class EditorDict(NodeDict):
    def __init__(self, nodeName=''):
        super(EditorDict, self).__init__(nodeName=nodeName)
        with self.attributeLock:
            self.manager    = EditorManager(self)

    def __setitem__(self, key, val):
        if not isinstance(val, EditorNode):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of EditorNode or of its subclasses.')
        if key != id(val):
            raise ValueError, 'The key should be identical to the ID of the editor.'
        super(EditorDict, self).__setitem__(key, val)

    def add(self, node):
        self[id(node)]  = node
        return id(node)
    
