
(require [wavesynlib.languagecenter.wavesynscript.macros [
    init-wavesynscript-macros
    BindLazyNode]])
(init-wavesynscript-macros)
(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import platform)
(import [importlib [import-module]])
(import [wavesynlib.languagecenter.wavesynscript [NodeDict]])



(defclass Toolboxes [NodeDict]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (when (= "windows" (.lower (platform.system) ) ) 
            (BindLazyNode
                self.msoffice [
                    wavesynlib.toolboxes.msoffice.modelnode
                    MSOffice]) ) ) 

    (defn --getitem-- [self toolbox-name]
        (when (in toolbox-name self)
            (return (.--getitem-- (super) toolbox-name)))
        (setv mod (import-module f".{toolbox-name}.toolboxnode" (.join "." (cut (.split --name-- ".") 0 -1)) ))
        (setv node (mod.ToolboxNode :toolbox-name toolbox-name))
        (assoc self toolbox-name node)
        node ) 
        
    (defn -make-child-path [self child]
        f"{self.node-path}[{(repr child.-toolbox-name)}]")
        
    (defn -hy-make-child-path [self child]
        ; (
        f"{(cut self.hy-node-path 0 -1)} [{(repr child.-toolbox-name)}])") )
