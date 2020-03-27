from tkinter import Frame, Text, Toplevel
from tkinter.filedialog import askdirectory

import os
import sys
import platform
from importlib import import_module

from wavesynlib.languagecenter.designpatterns import Observable
from .scrolledlist import ScrolledList



class DirIndicator(Frame, Observable):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        self._text = text = Text(self, wrap='none', height=1.2, relief='solid')
        text.bind('<Configure>', self._on_resize)
        text.bind('<KeyPress>', self._on_key_press)
        text.pack(fill='x', expand='yes', side='left')
        self._default_cursor = text['cursor']
        self._default_background_color = text['background']

        # History
        self._history = []
        text.tag_config('back_button', foreground='grey')
        text.tag_bind('back_button', '<Button-1>', self._on_back_click)
        text.tag_bind('back_button', '<Button-3>', self._on_back_right_click)
        text.tag_bind('back_button', '<Enter>',
                      lambda *args: self._change_cursor_to_hand(True))
        text.tag_bind('back_button', '<Leave>',
                      lambda *args: self._change_cursor_to_hand(False))
                      
        text.insert('1.0', u'\u2190 ', 'back_button')
        # End History

        # Browse Button
        text.tag_config('browse_button', foreground='orange')
        text.tag_bind('browse_button', '<Button-1>', self._on_button_click)
        text.tag_bind('browse_button', '<Enter>',
                      lambda *args: self._change_cursor_to_hand(True))
        text.tag_bind('browse_button', '<Leave>',
                      lambda *args: self._change_cursor_to_hand(False))
        # End Browse Button
                      
        # WinOpen Button
        sys_name = platform.system().lower()
        try:
            __mod = import_module(f'wavesynlib.interfaces.os.{sys_name}.shell.winopen')
            winopen_func = getattr(__mod, 'winopen')
            def on_winopen_click(*args):
                winopen_func(self._directory)
        except (ImportError, AttributeError):
            def on_winopen_click(*args):
                pass                      
                      
        text.tag_config('winopen_button', foreground='orange')
        text.tag_bind('winopen_button', '<Button-1>', on_winopen_click)
        text.tag_bind('winopen_button', '<Enter>',
                      lambda *args: self._change_cursor_to_hand(True))
        text.tag_bind('winopen_button', '<Leave>',
                      lambda *args: self._change_cursor_to_hand(False))    
        # End WinOpen Button
                
        self._blank_len = 2
        self._browse_text = u'\u25a1'
        self._winopen_text = u'\u25a0'
        self._coding = sys.getfilesystemencoding()
        self._directory = None
        
        
    def _on_back_click(self, *args):
        '''Triggered by clicking the BACK button.
Go back according to the self._history list.'''
        if len(self._history) > 1:
            del self._history[-1]
            self.change_dir(self._history[-1])
    
    
    def _on_back_right_click(self, *args):
        '''Triggered by right clicking the BACK button.
A menu displaying the browse history will pop up.'''
        if len(self._history) > 1:
            self._show_dir_list('', self._history, history_mode=True)
            
            
    def _on_winopen_click(self, *args):
        pass
    
                                
    def _on_button_click(self, *args):
        '''Triggered by clicking the BROWSER button.
A directory selector will popup.
'''
        directory   = askdirectory()
        if directory:
            self.change_dir(directory)
            
            
    def _on_resize(self, *args):
        self._text.see('end')
        self._text.mark_set('insert', 'end')


    def _change_cursor_to_hand(self, hand):
        text    = self._text
        if hand:
            text.config(cursor='hand2')
        else:
            text.config(cursor=self._default_cursor)
            

    def _on_folder_name_hover(self, tagName, enter=True, 
                              background_color='pale green'):
        '''Triggered by hovering the mouse pointer on a directory name.
Once triggered, the cursor will change to a hand icon, and the directory 
name will be highlighted.'''
        self._change_cursor_to_hand(enter)
        background_color = background_color if enter else \
            self._default_background_color
        self._text.tag_config(tagName, background=background_color) 
 

    def _show_dir_list(self, path, dir_name_list, history_mode=False, menu=[None]):
        '''Popup a "MENU" displaying a list of directory names.'''
        items = dir_name_list
        if items: # Not Empty
            # The position of the mouse pointer will be the position of the 
            # left corner of the popup MENU.
            x, y = self.winfo_pointerx(), self.winfo_pointery()
            menu_win = menu[0]
            if menu_win is not None:
                menu_win.destroy()
            # Utilizing a Toplevel without titlebar to mimic a popup menu
            menu_win = menu[0] = Toplevel()
            menu_win.wm_attributes('-topmost', True)
            # No Title bar
            menu_win.overrideredirect(1)
            if not path: # Todo: ScrolledList with horizontal scroll
                menu_width = 800
            else:
                menu_width = 200
            menu_win.geometry(f'{menu_width}x300+{x}+{y}')
            # Once the so called MENU loses focus, it will DISAPPEAR instantly.
            menu_win.bind('<FocusOut>', lambda evt: menu_win.destroy())
            itemList = ScrolledList(menu_win)
            itemList.pack(expand='yes', fill='both')
            itemList.list.focus_set()
            for item in items:
                itemList.append(item)
                
            def on_list_click(index, label):
                if not history_mode:
                    full_path = os.path.join(path, label)
                else:
                    # History mode. Triggered by right click the BACK button.
                    # Refresh the history list.
                    self._history = self._history[:(index+1)]
                    full_path = self._history[-1]
                self.change_dir(full_path)
                # Once the user selected a directory, the MENU should disappear
                # immediately.
                menu_win.destroy()
                
            itemList.list_click_callback  = on_list_click
       
        
    def _on_seperator_click(self, evt, path):
        '''Triggered by clicking the path seperator.
A menu displaying directory names will popup. User can select a directory by 
clicking its name.'''
        items = [item for item in os.listdir(path) if 
                 os.path.isdir(os.path.join(path, item))]
        self._show_dir_list(path, items)
        
                                  
    def _on_key_press(self, evt):
        rend, cend = self._text.index('end-1c').split('.')
        cend = int(cend)
        r, c = self._text.index('insert').split('.')
        c = int(c)
        # Suppress key inputs if cursor is located at special characters which 
        # form the BROWSE button and the BACK button
        if c > cend - self._blank_len - len(self._browse_text) - len(self._winopen_text) or c < 3:
            if evt.keysym not in ('Left', 'Right', 'Up', 'Down'):
                return 'break'
        
        # \n will trigger the change dir action
        if evt.keysym == 'Return': 
            path = self._get_path()
            # Check the validity of the path
            if os.path.exists(path):
                self.change_dir(path)
            # If the path is not valid, return to the previous path
            else:
                self._refresh()
            # Not pass the event to the next handler.
            return 'break' 

            
    def _get_path(self):
        # 1.2 simply remove the characters forming the BACK button.
        path = self._text.get('1.2', 'end')
        # Remove the characters forming the BROWSER button.
        path = path[:-(self._blank_len + len(self._browse_text) + len(self._winopen_text))]            
        return path
        
            
    def _refresh(self):
        text = self._text
        directory = self._directory

        text.delete('1.2', 'end')
        folderList  = directory.split(os.path.sep)
        cumPath     = ''
        for index, folder in enumerate(folderList):
            if not isinstance(folder, str):
                folder = folder.decode(self._coding, 'ignore')
            cumPath += folder + os.path.sep 
            
            # Configure folder name
            tagName     = f'folder_name_{str(index)}'
            text.tag_config(tagName)
            text.tag_bind(tagName, '<Button-1>', 
                          lambda evt, cumPath=cumPath: self.change_dir(cumPath))
            text.tag_bind(tagName, '<Enter>', 
                          lambda evt, tagName=tagName: 
                              self._on_folder_name_hover(tagName, enter=True))
            text.tag_bind(tagName, '<Leave>', 
                          lambda evt, tagName=tagName: 
                              self._on_folder_name_hover(tagName, enter=False))
            text.insert('end', folder, tagName)
            # 'end' Configure folder name
            
            # Configure folder sep
            sepName = f'sep_tag_{str(index)}'                
            text.tag_config(sepName)
            text.tag_bind(sepName, '<Button-1>', 
                          lambda evt, cumPath=cumPath: 
                              self._on_seperator_click(evt, cumPath))
            text.tag_bind(sepName, '<Enter>', 
                          lambda evt, tagName=sepName: 
                          self._on_folder_name_hover(tagName, 
                                                     enter=True, 
                                                     background_color='orange'))
            text.tag_bind(sepName, '<Leave>', 
                          lambda evt, tagName=sepName: 
                              self._on_folder_name_hover(tagName, 
                                                         enter=False, 
                                                         background_color='orange'))
            text.insert('end', os.path.sep, sepName)
            # END Configure folder sep
        

        text.insert('end', ' '*self._blank_len)
        text.insert('end', self._browse_text, 'browse_button') 
        text.insert('end', self._winopen_text, 'winopen_button')
        

    def change_dir(self, dirname):
        dirname = os.path.abspath(dirname)        
        self._directory = dirname
        self._refresh()
        self.notify_observers(dirname)
        if len(self._history) == 0:
            self._history.append(dirname)
        if dirname != self._history[-1]:
            self._history.append(dirname)
            if len(self._history) > 16:
                del self._history[0]
        if len(self._history) > 1:
            forecolor = 'forestgreen'
        else:
            forecolor = 'grey'
        self._text.tag_config('back_button', foreground=forecolor)
                
                
    @property
    def directory(self):
        return self._directory
