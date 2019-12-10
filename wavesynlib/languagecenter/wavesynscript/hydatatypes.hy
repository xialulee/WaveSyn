(require [hy.contrib.loop [loop]])
(require [hy.extra.anaphoric [%]])
(require [wavesynlib.languagecenter.hy.utils [defprop dyn-setv]])

(import [importlib [import-module]])
(import [wavesynlib.languagecenter.designpatterns [Observable]])



(defclass -ModelTreeMonitor [Observable]
    (defn --init-- [self]
        (.--init-- (super) ) ) 
        
    (defn -on-add-node [self node]
        (.notify-observers self node "add") ) 
        
    (defn -on-remove-node [self node]
        (.notify-observers self node "remove") ) )

(setv model-tree-monitor (-ModelTreeMonitor) )



; How to implement a context manager? See:
; http://pypix.com/python/context-managers/        
(defclass AttributeLock []
    (defn --init-- [self node]
        (.--init-- (super) ) 
        (unless (instance? ModelNode node) 
            (raise (TypeError "Only the instance of ModelNode is accepted.") ) ) 
        (setv self.node node) ) 
        
    (defn --enter-- [self]
        (setv (. self node attribute-auto-lock) True) 
        self.node) 
        
    (defn --exit-- [self &rest dumb]
        (setv (. self node attribute-auto-lock) False) ) )



; To Do: Implement an on_bind callback which is called when a node is connecting to the tree.    
(defclass ModelNode []
    [-xmlrpcexport- []]
    
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) ) 
        (setv 
            node-name (.get kwargs "node_name" "") 
            is-root   (.get kwargs "is_root"   False) 
            is-lazy   (.get kwargs "is-lazy    False") ) 
        (unless (in "_attribute_lock" self.--dict--) 
            (comment "TO-DO: Maybe hasattr is better?")
            (.--setattr-- object self "_attribute_lock" (set) ) ) 
        (setv 
            self.parent-node None
            self.--is-root   is-root
            self.--is-lazy   is-lazy) 
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
if the following statements are executed:
with node.attribute_lock:
  node.a = 0
then node will have a property named 'a', which cannot be re-assigned."
            (AttributeLock self) ) ) 
            
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
            (loop [[node self]]
                (if node.is-root
                    node
                #_else
                    (recur node.parent-node) ) ) ) ) )



(defclass Constant []
"Constant type of wavesynscript."
    [--slots-- (, "__name" "__value" "__doc")
     --cache   {}]
    
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