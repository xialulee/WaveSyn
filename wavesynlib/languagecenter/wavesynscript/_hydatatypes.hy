(require [hy.contrib.loop [loop]])
(require [hy.extra.anaphoric [%]])
(require [wavesynlib.languagecenter.hy.utils [
    super-init make-slots defprop dyn-setv]])

(import [importlib [import-module]])
(import [wavesynlib.languagecenter.designpatterns [Observable]])
(import [wavesynlib.languagecenter.python.utils [get-module-path]])


(defclass -ModelTreeMonitor [Observable]
    (defn --init-- [self]
        (super-init) ) 
        
    (defn -on-add-node [self node]
        (.notify-observers self node "add") ) 
        
    (defn -on-remove-node [self node]
        (.notify-observers self node "remove") ) )

(setv model-tree-monitor (-ModelTreeMonitor) )



; How to implement a context manager? See:
; http://pypix.com/python/context-managers/        
(defclass AttributeLock []
    (defn --init-- [self node]
        (super-init) 
        (unless (instance? ModelNode node) 
            (raise (TypeError "Only the instance of ModelNode is accepted.") ) ) 
        (setv self.node node) ) 
        
    (defn --enter-- [self]
        (setv (. self node attribute-auto-lock) True) 
        self.node) 
        
    (defn --exit-- [self &rest dumb]
        (setv (. self node attribute-auto-lock) False) ) )



(defclass ModelNode []
    (setv -xmlrpcexport- [])
    
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init) 
        (setv 
            node-name (.get kwargs "node_name" "") 
            is-root   (.get kwargs "is_root"   False) 
            is-lazy   (.get kwargs "is_lazy"   False) ) 
        (unless (hasattr self "_attribute_lock")
            ; TO-DO: Maybe hasattr is better?
            (.--setattr-- object self "_attribute_lock" (set) ) ) 
        (setv 
            self.parent-node    None
            self.--root-node    None
            self.--node-path    None
            self.--hy-node-path None
            self.--is-root      is-root
            self.--is-lazy      is-lazy) 
        (when is-lazy
            (comment "TO-DO: Use dyn-private-setv and loop instead.")
            (setv 
                self.--module-name  (.pop kwargs "module_name"  None) 
                self.--class-name   (.pop kwargs "class_name"   None) 
                self.--class-object (.pop kwargs "class_object" None) 
                self.--init-args    (.pop kwargs "init_args"    []) 
                self.--init-kwargs  (.pop kwargs "init_kwargs"  {}) ) ) 
        (setv self.node-name node-name) )  
        
    (defn lock-attribute [self attribute-name &optional [lock True]]
"Lock a specified attribute, i.e. the attribute cannot be re-assigned.
For example:        
node.a = 0
node.lock_attribute('a')
If you try to give node.a a new value
node.a = 1
then an AttributeError will be raised."
        (if lock 
            (.add self.-attribute-lock attribute-name) 
        #_else
            (if (in attribute-name self.-attribute-lock) 
                (.remove self.-attribute-lock attribute-name) ) ) ) 
                
    (defprop attribute_lock
        #_getter
        (fn [self] 
"This attribute is in fact a context manager.
If the following statements are executed:
with node.attribute_lock:
  node.a = 0
then node will have a property named 'a', which cannot be re-assigned."
            (AttributeLock self) ) ) 

    (defn on-connect [self])

    (defn --getattribute-- [self attribute-name]
        (setv attr (.--getattribute-- object self attribute-name) ) 
        (when (and (instance? ModelNode attr) attr.is-lazy) 
            (comment "Unlock the attribute name before replacing.") 
            (.lock-attribute self attribute-name :lock False) 
            (setv attr attr.real-node) 
            (comment "Replace the lazy node with the real one.") 
            (with [self.attribute-lock]
                (setattr self attribute-name attr) ) ) 
        attr) 

    (defn --setattr-- [self key val]
        (unless (in "_attribute_lock" self.--dict--) 
            ; This circumstance happens when __setattr__ called
            ; before __init__ being called.
            (.--setattr-- object self "_attribute_lock" (set) ) ) 
        (unless (in "attribute_auto_lock" self.--dict--) 
            (.--setattr-- object self "attribute_auto_lock" False) ) 
        (when (in key self.-attribute-lock) 
            (raise (AttributeError f"Attribute \"{key}\" is unchangeable.") ) ) 
        (when (and
                    (instance? ModelNode val) 
                    (not val.is-root) 
                    (is val.parent-node None) ) 
            (setv val.node-name (if val.node-name val.node-name key) ) 
            (.--setattr-- object val "parent_node" self) 
            ; The autolock mechanism will lock the node
            ; after you attach it to the model tree.
            ; A child node cannot change its parent.
            (.lock-attribute val "parent-node") 
            ; and the parent node's child node cannot be
            ; re-assigned.
            (.lock-attribute self key)
            (.-on-add-node model-tree-monitor val) ) 
        (.--setattr-- object self key val) 
        (when (and 
                    self.attribute-auto-lock 
                    ; attribute_auto_lock itself cannot be locked.
                    (!= key "attribute_auto_lock") ) 
            (.lock-attribute self key) ) 
        (when (instance? ModelNode val) 
            (.on-connect val) ) )
            
    (defprop is-root 
        #_getter
        #%(. %1 --is-root) ) 
        
    (defprop is-lazy 
        #_getter
        #%(. %1 --is-lazy) ) 

    (comment "Rename get-real-node (meth) to real-node (prop).")    
    (defprop real-node 
        #_getter
        (fn [self]
        "Initialize and return the real node of a lazy node."
            (setv node self) 
            (if self.is-lazy
                (if (is self.--class-object None) (do
                    (setv
                        mod  (import-module self.--module-name) 
                        node ((getattr mod self.--class-name) #* self.--init-args #** self.--init-kwargs ) ) ) 
                #_else
                    (setv node (.--class-object self #* self.--init-args #** self.--init-kwargs) ) ) ) 
            node) ) 

    (defn -make-child-path [self child]
        f"{self.node-path}.{child.node-name}")

    (defn -hy-make-child-path [self child]
        ; (
        f"{(cut self.hy-node-path 0 -1)} {child.node-name})")

    (defprop node-path
        #_getter
        (fn [self]
            (when (none? self.--node-path)
                (if self.is-root
                    (setv self.--node-path self.node-name) 
                #_else
                    (setv self.--node-path (.-make-child-path self.parent-node self) ) ) )
            self.--node-path) ) 

    (defprop hy-node-path
        #_getter
        (fn [self]
            (when (none? self.--hy-node-path) 
                (cond
                [self.is-root
                    (setv self.--hy-node-path f"(. {self.node-name})")]
                [True
                    (setv self.--hy-node-path (.-hy-make-child-path self.parent-node self) ) ]) )
            self.--hy-node-path) ) 

    (defprop child-nodes 
        #_getter
        (fn [self]
            (dfor 
                attribute-name self.--dict--
                :if (and 
                    (instance? ModelNode (. self --dict-- [attribute-name]) ) 
                    (!= attribute-name "parent_node") ) 
                [attribute-name (. self --dict-- [attribute-name] node-path)]) ) )
            
    (defprop root-node
        #_getter
        (fn [self]
            (if (none? self.--root-node)
                (setv self.--root-node (loop [[node self]]
                    (if node.is-root
                        node
                    #_else
                        (recur node.parent-node) ) ) ) ) 
            self.--root-node) ) 
            
    (defprop module-path
        #_getter
        (fn [self]
            (get-module-path self))) 
            
    (defn add-lazy-local-node [self node-name module-name class-name]
        (setattr 
            self 
            node-name
            (ModelNode 
                :is-lazy     True
                :module-name (/ self.module-path.parent module-name) 
                :class-name  class-name) ) ) ) 



(defclass NodeContainer [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) ) 
        
    (defn -make-child-path [self child]
        (raise (NotImplementedError "Subclass of NodeContainer should implement _make_child_path") ) ) 
        
    (defn -hy-make-child-path [self child]
        (raise (NotImplementedError "Subclass of NodeContainer should implement _hy_make_child_path") ) ) )



(defclass Dict [dict]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init) ) )



(defclass NodeDict [NodeContainer Dict]
    (setv -xmlrpcexport- []) 
    
    (defn --init-- [self &optional [node-name ""]]
        (super-init :node-name node-name) ) 
        
    (defn -make-child-path [self child]
        f"{self.node-path}[{(id child)}]") 
        
    (defn -hy-make-child-path [self child]
        ; (
        f"{(cut self.hy-node-path 0 -1)} [{(id child)}])") 
        
    (defn --setitem-- [self key child]
        (with [child.attribute-lock] 
            (setv child.parent-node self) )
        (.-on-add-node model-tree-monitor child) 
        (Dict.--setitem-- self key child) 
        (.on-connect child) ) 
        
    (defn --delitem-- [self key]
        (.-on-remove-node model-tree-monitor (get self key) ) 
        (Dict.--delitem-- self key) ) 
        
    (defn pop [self key]
        (.-on-remove-node model-tree-monitor (get self key) ) 
        (Dict.pop self key) ) )



(defclass Constant []
"Constant type of wavesynscript."
    (make-slots --name --value --doc)
    (setv --cache {})
    
    (defn --new-- [cls name &optional value doc]
        (if (in name cls.--cache) (do
            (setv c (. cls --cache [name]) ) 
            (if (!= value c.value) 
                (raise (ValueError "This constant has already been initialized with a different value.") ) ) 
            c) 
        #_else
            (.--new-- object cls) ) ) 
            
    (defn --init-- [self name &optional value doc]
        (unless (in name self.--cache) 
            (setv
                self.--name  name
                self.--value value
                self.--doc   doc
                (. self --cache [name]) self) ) ) 
                
    (defprop name 
        #_getter
        #%(. %1 --name) ) 
        
    (defprop value
        #_getter
        #%(. %1 --value) ) 
        
    (defprop doc
        #_getter
        #%(. %1 --doc) ) 
        
    (defn help [self] (print self.doc) ) )



(defclass Constants []
    (setv --name-value-pairs (,
        (, "KEYSYM-MODIFIERS" #{
            "Alt_L"     "Alt_R"
            "Control_L" "Control_R"
            "Shift_L"   "Shift_R" })
        (, "KEYSYM-CURSORKEYS" #{
            "KP_Prior" "KP_Next"  "KP_Home" "KP_End" 
            "KP_Left"  "KP_Right" "KP_Up"   "KP_Down" 
            "Left"     "Right"    "Up"      "Down" 
            "Home"     "End"      "Next"    "Prior"}) ) )

    (for [[name value] --name-value-pairs]
        (dyn-setv name (Constant name value) ) )
            
    #@(classmethod
    (defn append-new-constant [cls name &optional value doc]
        (setattr cls name (Constant name value doc) ) ) ) )
