(require [hy.extra.anaphoric [*]])
(import [abc [ABC abstractmethod]])



(defclass AbstractTreeNode [ABC]
    #@(abstractmethod
    (defn __iter__ [self])) 

    #@(abstractmethod
    (defn is-group [self]))
        
    #@(abstractmethod
    (defn make-group [self group-info]))
        
    #@(abstractmethod
    (defn make-leaf [self leaf-info])) )



(defn tree-trans [source dest]
    (ap-each source (cond
        [(.group? it)
            (tree-trans it (.make-group dest it) )]
        [True
            (.make-leaf dest it)]) ) )
