(require [wavesynlib.languagecenter.wavesynscript.macros [
    init-wavesynscript-macros
    BindLazyNode]])
(init-wavesynscript-macros)
(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import platform)
(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])
(import [wavesynlib.interfaces.editor.modelnode [EditorDict]])



(defclass Interfaces [ModelNode]
"The interfaces node of WaveSyn, which provides several mechanisms for
communicating with different software applications and hardware devices."
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (BindLazyNode
            [self.os 
                wavesynlib.interfaces.os.modelnode 
                OperatingSystem]
            [self.net 
                wavesynlib.interfaces.net.modelnode 
                Net]
            [self.gpu 
                wavesynlib.interfaces.gpu 
                GPU]
            [self.dotnet 
                wavesynlib.interfaces.dotnet 
                DotNet]
            [self.imagemagick 
                wavesynlib.interfaces.imagemagick
                ImageMagickNode]) 
        (setv self.editors (EditorDict) ) 
        (when (= "windows" (.lower (platform.system) ) ) 
            (BindLazyNode
                [self.msoffice
                    wavesynlib.interfaces.msoffice.modelnode
                    MSOffice]) ) ) )
