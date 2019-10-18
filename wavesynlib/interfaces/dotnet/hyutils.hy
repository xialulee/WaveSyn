(require [hy.extra.anaphoric [*]])

(import clr)
(import System)



(defn new [class-object &kwargs kwargs]
    (setv obj (class-object) ) 
    (for [[key val] (.items kwargs)] 
        (setattr obj key val) ) 
    obj)



(defclass MemoryStreamWrapper [] 
    (defn --init-- [self]
        (import [System.IO [MemoryStream]]) 
        (setv self.--stream (MemoryStream) ) ) 
        
    (defn write [self data]
        (.Write self.--stream data 0 (len data) ) ) 
        
    (defn seek [self offset &optional [whence 0]]
        (.Seek self.--stream offset whence) ) 
        
    #@(property
    (defn real-object [self]
        self.--stream) ) )



(defclass BitmapUtils []
    #@(staticmethod
    (defn pil-to-netbmp [image]
        (import [System.Drawing [Bitmap]]) 
        (setv ms (MemoryStreamWrapper) ) 
        (.save image ms "png") 
        (.seek ms 0) 
        (Bitmap ms.real-object) ) )

    #@(staticmethod
    (defn netbmp-to-pil [bitmap]
        (import [PIL [Image]]) 
        (setv stream (BitmapUtils.netbmp-to-pystream bitmap) ) 
        (Image.open stream) ) )

    #@(staticmethod
    (defn netbmp-to-pystream [bitmap]
        (import [System.IO [MemoryStream]]) 
        (import [System.Drawing.Imaging [ImageFormat]]) 
        (setv ms (MemoryStream) ) 
        (.Save bitmap ms ImageFormat.Png) 
        (setv arr (.ToArray ms) ) 
        (import [io [BytesIO]]) 
        (setv stream (BytesIO) ) 
        (.write stream (bytes arr) ) 
        (.seek stream 0) 
        stream) )

    #@(staticmethod
    (defn netbmp-to-matrix [bitmap]
        (setv stream (BitmapUtils.netbmp-to-pystream bitmap) ) 
        (import [imageio [imread]]) 
        (imread stream "png") ) ) ) 
