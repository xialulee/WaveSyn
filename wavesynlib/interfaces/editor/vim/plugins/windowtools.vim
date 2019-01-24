py3 << EOF
import vim
import ctypes
import win32con

def set_topmost(b):
'''Make (or cancel) the Vim window TOPMOST.
b: b!=0 means make the window topmost,
   b==0 means make the window not topmost. 
'''
    user32 = ctypes.windll.user32
    GetForegroundWindow = user32.GetForegroundWindow
    SetWindowPos = user32.SetWindowPos
    if b == 0:
        b = win32con.HWND_NOTOPMOST
    else: 
        b = win32con.HWND_TOPMOST

    SetWindowPos(
        GetForegroundWindow(), 
        b,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)



def set_opacity(hwnd, alpha):
'''Set the opacity of the Vim window.
Based on the implementation of vimtweak.

hwnd: The handle of the Vim window.
alpha: 0   for completely transparent,
       255 for opaque.'''
    user32 = ctypes.windll.user32
    SetWindowLong = user32.SetWindowLongW
    GetWindowLong = user32.GetWindowLongW
    SetLayeredWindowAttributes = user32.SetLayeredWindowAttributes

    if alpha == 255:
        SetWindowLong(
            hwnd, 
            win32con.GWL_EXSTYLE,
            GetWindowLong(
                hwnd, 
                win32con.GWL_EXSTYLE) & ~win32con.WS_EX_LAYERED)
    else:
        SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            GetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)



def set_opacity_gui():
    import tkinter
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    def on_move(alpha):
        alpha = int(alpha)
        alpha = int(alpha/100*255)
        set_opacity(hwnd, alpha)
    root = tkinter.Tk()
    tkinter.Label(
        root,
        text="Use the following scale widgets to adjust opacity of Vim window.").pack()
    scale_alpha = tkinter.Scale(
        root, 
        from_=10,
        to=100,
        orient="horizontal",
        command=on_move)
    scale_alpha.pack()
    scale_alpha.set(100)
    root.title("Set Opacity")
    root.mainloop()
EOF



function! Topmost(b)
    py3 set_topmost(int(vim.eval("a:b")))
endfunction




function! SetOpacity(alpha)
py3 << EOF
set_opacity(
    ctypes.windll.user32.GetForegroundWindow(),
    int(int(vim.eval('a:alpha'))/100*255))
EOF
endfunction



function! SetOpacityGUI()
    py3 set_opacity_gui()
endfunction
