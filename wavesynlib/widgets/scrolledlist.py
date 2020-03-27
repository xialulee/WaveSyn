from tkinter import Frame, Listbox
from tkinter.ttk import Scrollbar

from wavesynlib.languagecenter.utils import MethodDelegator



class ScrolledList(Frame):
    method_name_map   = {
        'insert':'insert', 
        'delete':'delete', 
        'activate':'activate',
        'selection_set':'selection_set',
        'selection_clear':'selection_clear',
        'see':'see',
        'item_config':'itemconfig',
        'list_config':'config'
    }
    
    for method_name in method_name_map:
        locals()[method_name] = MethodDelegator('list', 
                                                method_name_map[method_name])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sbar = Scrollbar(self)
        list = Listbox(self)
        sbar.config(command=list.yview)
        list.config(yscrollcommand=sbar.set)
        sbar.pack(side='right', fill='y')
        list.pack(side='left', expand='yes', fill='both')
        list.bind('<<ListboxSelect>>', self._on_listbox_click)
        
        self.__list_click_callback = None
        self.__list = list
        self.__sbar = sbar
        

    @property
    def list(self):
        return self.__list
    

    @property
    def sbar(self):
        return self.__sbar
    

    def clear(self):
        self.__list.delete(0, 'end')
        
                
    @property
    def current_selection(self):
        return self.__list.curselection()
    
    
    @property
    def current_data(self):
        retval = [self.list.get(index) for index in self.current_selection]
        return retval
    
    
    def append(self, item):
        self.__list.insert('end', item)
        
        
    @property
    def length(self):
        # Don't plus one. END points to the next position of the tail element.
        return self.list.index('end')
    
        
    @property
    def list_click_callback(self):
        return self.__list_click_callback
    

    @list_click_callback.setter
    def list_click_callback(self, val):
        if not callable(val):
            raise TypeError
        self.__list_click_callback = val
        

    def _on_listbox_click(self, event):
        index = self.__list.curselection()
        if len(index) > 0:
            index = index[0]
            label = self.__list.get(index)
            if self.list_click_callback:
                self.list_click_callback(index, label)
                
