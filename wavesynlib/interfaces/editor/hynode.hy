(require [hy.extra.anaphoric [*]])
(require [wavesynlib.languagecenter.hy.utils [call=]])

(import os)
(import tempfile)
(import subprocess)

(import [wavesynlib.languagecenter.wavesynscript [Scripting ModelNode NodeDict]])
(import [wavesynlib.languagecenter.designpatterns [Observable]])



(defclass EditorNode [ModelNode]
    (defn --init-- [self &optional [node-name ""] [editor-path ""]]
        (.--init-- (super) :node-name node-name) 
        (with [self.attribute-lock]
            (setv self.editor-path editor-path) ) 
        (setv 
            self.--thread None
            self.code     None) ) 
            
    (defn launch [self &optional [code ""] file-path [run-on-exit True]]
        (if self.--thread
            (raise (Exception "Editor has already been launched.") ) ) 
        (setv self.--run-on-exit run-on-exit) 
        (if-not file-path (do
            (setv [fd filename] 
                (tempfile.mkstemp 
                    :suffix ".py" 
                    :text True) ) 
            (with [f (os.fdopen fd "w")]
                ; Close the temp file, consequently the external editor can edit it without limitations.
                (if code (.write f code) ) ) 
            (setv self.--is-temp True) ) 
        #_else 
            (setv 
                self.--is-temp False
                filename       (str file-path) ) 
            ) 
        (with [self.attribute-lock]
            (setv self.filename filename) ) 
        (setv self.--thread
            (.create-thread-object self.root-node.thread-manager
                #%(subprocess.call [self.editor-path self.filename]) ) ) 
        (.start self.--thread) ) 
        
    #@(property
    (defn is-temp-file [self]
        self.--is-temp) )
        
    #@(property
    (defn run-on-exit [self]
        self.--run-on-exit))
        
    (defn is-alive [self]
        (setv alive (.alive? self.--thread) ) 
        (when (and (not alive) (none? self.code)) 
            (try
                (with [f (open self.filename "r")]
                    (setv self.code (.read f)) ) 
            (finally
                (when self.is-temp-file
                    (os.remove self.filename) ) ) ) ) 
        alive) )



(defclass EditorManager [Observable]
    (defn --init-- [self editor-dict]
        (.--init-- (super)) 
        (setv self.--editor-dict editor-dict)) 
        
    (defn update [self]
        (when self.--editor-dict
            (for [[key editor] (.items self.--editor-dict)]
                (unless (.alive? editor) 
                    (.notify-observers self editor) 
                    (.pop self.--editor-dict key) 
                    (break) ) ) ) ) )



(defclass EditorDict [NodeDict]
    (defn --init-- [self &optional [node-name ""]]
        (.--init-- (super) :node-name node-name) 
        (with [self.attribute-lock]
            (setv self.manager (EditorManager self) ) ) ) 
            
    (defn --setitem-- [self key val]
        (unless (instance? EditorNode val) 
            (raise (TypeError f"{self.node-path} only accepts instances of EditorNode or its subclasses.") )) 
        (if (!= key (id val)) 
            (raise (TypeError "The key should be identical to the ID of the editor.") ) ) 
        (.--setitem-- (super) key val) )
        
    (defn add [self node]
        (setv id-node (id node) )
        (setv (. self [id-node]) node) 
        id-node)
        
    #@(Scripting.printable
    (defn launch [self &optional editor-path [code ""] file-path [run-on-exit False]]
        "Launch a specified editor. When the editor terminated, it will notify the observer of .manager.
  editor_path: String. Specify the path of the editor. If None is given, it will launch the one specified in config.json.
  code: A string representing the code to be edited, or the CLIPBOARD_TEXT const.
  file_path: a path of a file or a list of paths of several files, or the CLIPBOARD_PATH_LIST const.
  run_on_exit: run the content of the editor while the editor terminates."
        (unless editor-path
            (setv editor-path (. self root-node editor-info ["Path"]) ) ) 
        (call= 
            code 
            self.root-node.interfaces.os.clipboard.constant-handler-CLIPBOARD-TEXT)  
        (call=
            file-path
            self.root-node.interfaces.os.clipboard.constant-handler-CLIPBOARD-PATH-LIST) 
        (if (none? file-path) 
            (setv file-path [None]) ) 
        (if (instance? str file-path) 
            (setv file-path [file-path]) ) 
        (setv id-list []) 
        (ap-each file-path 
            (setv 
                editor-id 
                (.add self (EditorNode 
                    :editor-path editor-path) ) ) 
            (.launch (. self [editor-id]) 
                :code        code 
                :file-path   it 
                :run-on-exit run-on-exit) 
            (.append id-list editor-id) ) 
        id-list) ) 
        
    #@(Scripting.printable
    (defn launch-gvim [self &optional [code ""] file-path [run-on-exit False]]
        (.launch self 
            :editor-path "gvim" 
            :code        code 
            :file-path   file-path 
            :run-on-exit run-on-exit) ) ) )

