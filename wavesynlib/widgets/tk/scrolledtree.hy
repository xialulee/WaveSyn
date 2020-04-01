(require [hy.extra.anaphoric [*]])
(require [wavesynlib.languagecenter.hy.utils [defprop super-init]])

(import [tkinter [Frame Tk]])
(import [tkinter.ttk [Scrollbar Treeview]])

(import [wavesynlib.languagecenter.utils [FunctionChain MethodDelegator]])



(defclass ScrolledTree [Frame]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (.pack self :expand "yes" :fill "both") 
        (.-make-widgets self) 
        (setv self.--on-item-double-click (FunctionChain) ) 
        (.bind self.tree
            "<Double-1>"
            (fn [event]
                (setv item-id (.identify self.tree "item" event.x event.y) ) 
                (setv item-properties (.item self.tree item-id) )
                (.--on-item-double-click self item-id item-properties) ) ) )
                
    (defn clear [self]
        (ap-each (.get-children self.tree) (.delete self.tree it) ) ) 

    (defn hide-icon-column [self]
        (assoc self.tree "show" "headings") )
        
    (defprop on-item-double-click
        #_getter
        (fn [self] self.--on-item-double-click) ) 

    (defn load-dataframe [self dataframe]
        (.clear self)
        (setv (. self tree ["columns"]) (tuple dataframe.columns))
        (for [colname dataframe.columns]
            (.heading self colname :text colname))
        (for [row (.iterrows dataframe)]
            (.insert self 
                "" "end" 
                :text (first row) 
                :values (tuple (second row)))))
        
    (defn -make-widgets [self]
        (setv
            sbar (Scrollbar self) 
            tree (Treeview self) ) 
        (.config sbar :command tree.yview) 
        (.config tree :yscrollcommand sbar.set) 
        (.pack sbar :side "right" :fill "y") 
        (.pack tree :side "left" :expand "yes" :fill "both") 
        (setv self.tree tree) ) 
        
    (ap-each (, 
            "bind" 
            "insert"
            "delete"
            "heading"
            "selection"
            "item")
        (assoc (locals) it (MethodDelegator "tree" it) ) ) )



(defmain [&rest args]
    (import [pandas [DataFrame]])
    (setv df (DataFrame 
        :data [[1 2] [3 4]]
        :index ["row1" "row2"]
        :columns ["col1" "col2"]))
    (setv root (Tk))
    (setv st (ScrolledTree root))
    (.pack st)
    (.load-dataframe st df)
    (.mainloop root))

    

;from tkinter import Frame
;from tkinter.ttk import Scrollbar, Treeview

;from wavesynlib.languagecenter.utils import FunctionChain, MethodDelegator



;class ScrolledTree(Frame):
    ;def __init__(self, *args, **kwargs):
        ;super().__init__(*args, **kwargs)
        ;self.pack(expand='yes', fill='both')
        ;self._make_widgets()
        ;self.__on_item_double_click = FunctionChain()
        ;def dbclick_callback(event):
            ;item_id = self.tree.identify('item', event.x, event.y)
            ;item_properties = self.tree.item(item_id)
            ;self.__on_item_double_click(item_id, item_properties)
        ;self.tree.bind('<Double-1>', dbclick_callback)
        
        
    ;def clear(self):
        ;for row in self.tree.get_children():
            ;self.tree.delete(row)
        
        
    ;@property
    ;def on_item_double_click(self):
        ;return self.__on_item_double_click
        
    ;def _make_widgets(self):
        ;sbar    = Scrollbar(self)
        ;tree    = Treeview(self)
        ;sbar.config(command=tree.yview)
        ;tree.config(yscrollcommand=sbar.set)
        ;sbar.pack(side='right', fill='y')
        ;tree.pack(side='left', expand='yes', fill='both')
        ;self.tree   = tree
                
    ;for method_name in (
            ;'bind',
            ;'insert', 
            ;'delete',
            ;'heading',
            ;'selection',
            ;'item'
    ;):
        ;locals()[method_name] = MethodDelegator('tree', method_name)
