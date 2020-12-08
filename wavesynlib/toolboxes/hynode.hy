
(require [wavesynlib.languagecenter.wavesynscript.macros [
    init-wavesynscript-macros
    BindLazyNode]])
(init-wavesynscript-macros)
(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import platform)
(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])
(import [wavesynlib.interfaces.editor.modelnode [EditorDict]])



(defclass Toolboxes [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (when (= "windows" (.lower (platform.system) ) ) 
            (BindLazyNode
                self.msoffice [
                    wavesynlib.toolboxes.msoffice.modelnode
                    MSOffice]) ) ) )
