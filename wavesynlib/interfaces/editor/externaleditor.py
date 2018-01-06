from wavesynlib.languagecenter.wavesynscript  import ModelNode, NodeDict
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.languagecenter.utils          import eval_format

import subprocess
import tempfile
import os


        
class EditorNode(ModelNode):
    def __init__(self, node_name='', editor_path=''):
        ModelNode.__init__(self, node_name=node_name)
        with self.attribute_lock:
            self.editor_path = editor_path
        self.__thread   = None
        self.code       = None

    def launch(self):
        if self.__thread is not None:
            raise Exception('Editor has already been launched.')
        fd, filename    = tempfile.mkstemp(suffix='.py', text=True)
        with os.fdopen(fd):
            # Close the temp file, consequently the external editor can edit it without limitations.
            pass
        with self.attribute_lock:
            self.filename   = filename

        @self.root_node.thread_manager.create_thread_object
        def editor_thread():
            subprocess.call([self.editor_path, self.filename])
            
        self.__thread = editor_thread
        self.__thread.start()
        

    def is_alive(self):
        alive   = self.__thread.is_alive()
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
            for key in self.__editorDict:
                editor = self.__editorDict[key]
                if not editor.is_alive():
                    self.notify_observers(editor)
                    self.__editorDict.pop(id(editor))
                    break


class EditorDict(NodeDict):
    def __init__(self, node_name=''):
        super().__init__(node_name=node_name)
        with self.attribute_lock:
            self.manager = EditorManager(self)

    def __setitem__(self, key, val):
        if not isinstance(val, EditorNode):
            raise TypeError(eval_format('{self.node_path} only accepts instance of EditorNode or of its subclasses.'))
        if key != id(val):
            raise ValueError('The key should be identical to the ID of the editor.')
        super().__setitem__(key, val)

    def add(self, node):
        self[id(node)]  = node
        return id(node)
    
