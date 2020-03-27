from tkinter import Frame, IntVar
from tkinter.ttk import Scrollbar

from .textwinhotkey import TextWinHotkey

__DEBUG__ = False



class ScrolledText(Frame):
    '''This class is based on Programming Python 3rd Edition P517'''
    def __init__(self, 
                 parent=None, text='', file=None, horizontal_scroll=False):
        super().__init__(parent)
        self.pack(expand='yes', fill='both')
        self.make_widgets(horizontal_scroll=horizontal_scroll)
        self.set_text(text, file)
        self.__link_tag_functions = {}
        self.__disable_keys = False
        self.auto_url_link = False
        self.text_widget.bind('<KeyPress>', self._on_key_press)
        self.on_url_link_click = lambda dumb: None
        
        
    def make_widgets(self, horizontal_scroll=False):
        text = TextWinHotkey(self, relief='sunken')
        
        ybar = Scrollbar(self)        
        ybar.config(command=text.yview)
        ybar.pack(side='right', fill='y')
        
        if horizontal_scroll:
            xbar = Scrollbar(self)
            xbar.config(command=text.xview, orient='horizontal')
            xbar.pack(side='bottom', fill='x')
            text.config(xscrollcommand=xbar.set)
            
        text.config(yscrollcommand=ybar.set)  
        
        text.pack(side='left', expand='yes', fill='both')      
        self.text   = text # To Do: change the attribute name. 
        
        
    @property
    def disable_keys(self):
        return self.__disable_keys
        
    @disable_keys.setter
    def disable_keys(self, val):
        self.__disable_keys = val
        
        
    def _on_key_press(self, evt):
        if self.__disable_keys:
            return 'break'
        
        
    @property
    def text_widget(self):
        return self.text
    
    
    def see(self, *args, **kwargs):
        self.text.see(*args, **kwargs)
        

    def set_text(self, text='', file=None, *tags):
        # To Do: support auto url link
        if file:
            with open(file, 'r') as f:
                text = f.read().decode('gbk')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', text, *tags)
        self.text.mark_set('insert', '1.0')
        self.text.focus()
        
        
    def clear(self):
        self.set_text()
        widget = self.text_widget
        for key in self.__link_tag_functions:
            widget.tag_delete(widget)
        self.__link_tag_functions.clear()


    def append_text(self, text='', *tags):
        start = self.text_widget.index('end-1c')
        self.text.insert('end', text, *tags)
        stop = self.text_widget.index('end')
        if self.auto_url_link:
            self.__create_link_for_url(start, stop)
        

    def get_text(self):
        return self.text.get('1.0', 'end'+'-1c')
        

    def select_all(self):
        return self.text.select_all()
        

    def find_text(self, target):
        if target:
            where = self.text.search(target, 'insert', 'end')
            if where:
                if __DEBUG__:
                    print(f'Ctrl+F: searching for {target}')
                    print('position', where)
                pastit = where + f'+{len(target)}c'
                self.text.tag_remove('sel', '1.0', 'end')
                self.text.tag_add('sel', where, pastit)
                self.text.mark_set('insert', pastit)
                self.text.see('insert')
                self.text.focus()
                return True
            else:
                return False
        else:
            return False
            
            
    def create_link_tag(self, command, original_cursor='xterm'):
        tag_name = 'link' + str(id(command))
        widget = self.text_widget
        widget.tag_config(tag_name, underline=1, foreground='blue')
        widget.tag_bind(tag_name, '<Button-1>', command)
        widget.tag_bind(tag_name, '<Enter>', lambda dumb: widget.config(cursor='hand2'))
        widget.tag_bind(tag_name, '<Leave>', lambda dumb: widget.config(cursor=original_cursor))
        self.__link_tag_functions[tag_name] = command
        return tag_name
        
        
    def __create_link_for_url(self, start, stop):        
        c = IntVar()
        target = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        while True:
            where = self.text_widget.search(
                target, 
                start,
                stop,
                count=c,
                regexp=True
            )
            if not where:
                break
            pastit = where + ('+%dc' % c.get())
            urlstr = self.text_widget.get(where, pastit)
            tag_name = self.create_link_tag(
                lambda event, urlstr=urlstr: self.on_url_link_click(urlstr))
            self.text_widget.tag_add(tag_name, where, pastit)
            if self.text_widget.compare(pastit, '<', stop):
                start = pastit
                