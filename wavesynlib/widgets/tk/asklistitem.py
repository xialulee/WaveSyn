from tkinter import Frame, Toplevel
from tkinter.ttk import Button, Label, Combobox



def ask_list_item(the_list, default_item_index=0, message=''):
    win = Toplevel()

    Label(win, text=message).pack()

    combo = Combobox(win, stat='readonly')
    combo['values'] = the_list
    combo.current(default_item_index)
    combo.pack()
    
    ret = [None]
    
    def on_ok():
        ret[0] = combo.get()
        win.quit()
        
    def on_cancel():
        win.quit()
        
    frame = Frame(win)
    frame.pack()
    Button(win, text='Cancel', command=on_cancel).pack(side='right')            
    Button(win, text='Ok', command=on_ok).pack(side='right')
        
    win.protocol('WM_DELETE_WINDOW', win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    
    return ret[0]               
