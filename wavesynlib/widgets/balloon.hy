(require [wavesynlib.languagecenter.hy.utils [defprop]])

(import [tkinter [Toplevel]])
(import [tkinter.ttk [Label]])



(defclass Balloon []
"Balloon implementation which is compatible with the original Tix one.
Based on this post: http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml."
    (defclass Tip []
        (defn --init-- [self parent text]
            (setv 
                self.tip-widget      None
                self.parent          parent
                self.text            text
                self.--show-callback (fn [] "")))
                
        (defprop show-callback
            #_getter
            (fn [self]
                self.--show-callback) 
            #_setter
            (fn [self func]
                (unless (callable func) 
                    (raise "show_callback should be callable.") ) 
                (setv self.--show-callback func) ) ) 
                
                
        (defn show [self]
            (setv parent self.parent) 
            (setv text (+ self.text (self.show-callback)))
            (setv [x y cx cy] (.bbox parent "insert") ) 
            (setv x (+ x (.winfo-rootx parent) 27) )
            (setv y (+ y cy (.winfo-rooty parent) 27) ) 
            (setv tipw (Toplevel self.parent) ) 
            (setv self.tip-widget tipw)
            (.wm-overrideredirect tipw 1) 
            (.wm-geometry tipw f"+{x}+{y}")
            (.pack 
                (Label tipw 
                    :text text
                    :justify "left"
                    :background "#ffffe0"
                    :relief "solid"
                    :borderwidth 1
                    :font (, "tahoma" "8" "normal") ) 
                :ipadx 1) )
                
                
        (defn hide [self]
            (setv tipw self.tip-widget)
            (setv self.tip-widget None) 
            (when tipw
                (.destroy tipw) ) ) )
                
                
    (defn --init-- [self &rest args &kwargs kwargs]) 
    
    
    (defn bind-widget [self widget balloonmsg]
        (setv tip (.Tip self widget balloonmsg) )
        (.bind widget "<Enter>" (fn [event]
            (.show tip) ) ) 
        (.bind widget "<Leave>" (fn [event]
            (.hide tip) ) ) 
        tip) )




;from tkinter import Toplevel
;from tkinter.ttk import Label



;class Balloon:
    ;'''Balloon implementation which is compatible with the original Tix one.
;Based on this post: http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml.
;'''
    ;class Tip:
        ;def __init__(self, parent, text):
            ;self.tip_widget = None
            ;self.parent = parent
            ;self.text = text
            ;self.__show_callback = lambda: ""
        

        ;@property
        ;def show_callback(self):
            ;return self.__show_callback


        ;@show_callback.setter
        ;def show_callback(self, func):
            ;if not callable(func):
                ;raise ValueError("show_callback should be callable.")
            ;self.__show_callback = func

        
        ;def show(self):
            ;parent = self.parent
            ;text = self.text + self.show_callback()
            ;x, y, cx, cy = parent.bbox('insert')
            ;x = x + parent.winfo_rootx() + 27
            ;y = y + cy + parent.winfo_rooty() +27
            ;self.tip_widget = tipw = Toplevel(self.parent)
            ;tipw.wm_overrideredirect(1)
            ;tipw.wm_geometry("+%d+%d" % (x, y))
            ;Label(tipw, text=text, justify='left',
                  ;background="#ffffe0", relief='solid', borderwidth=1,
                  ;font=("tahoma", "8", "normal")).pack(ipadx=1)
            
            
        ;def hide(self):
            ;tipw = self.tip_widget
            ;self.tip_widget = None
            ;if tipw:
                ;tipw.destroy()
            
    
    ;def __init__(self, *args, **kwargs):
        ;pass
        
            
    ;def bind_widget(self, widget, balloonmsg):
        ;tip = self.Tip(widget, balloonmsg)
        
        ;def enter(event):
            ;tip.show()
            
        ;def leave(event):
            ;tip.hide()
            
        ;widget.bind('<Enter>', enter)
        ;widget.bind('<Leave>', leave)
        
        ;return tip