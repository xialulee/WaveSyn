# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 22:53:10 2017

@author: Feng-cong Li
"""

import wx
import wx.html


class CodeFrame(wx.Frame):
    def __init__(self, parent=None, id=-1, pos=wx.DefaultPosition, title='CF_HTML Edit', size=(800, 600)):        
        wx.Frame.__init__(self, parent, id, title, pos, size)
        sizer = wx.GridSizer(rows=1, cols=2)
        panel_left = wx.Panel(self, -1)

        vbox_left = wx.BoxSizer(wx.VERTICAL)
        code_text = self.__code_text = wx.TextCtrl(panel_left, -1, "Input HTML code here.", style=wx.TE_MULTILINE)
        code_text.SetInsertionPoint(0)
        code_text.Bind(wx.EVT_KEY_UP, self.on_char)
        button_clear = wx.Button(panel_left, -1, 'Clear')
        self.Bind(wx.EVT_BUTTON, self.on_clear_click, button_clear)
                
        vbox_left.Add(code_text, 1, wx.EXPAND)
        vbox_left.Add(button_clear)
                
        panel_left.SetSizer(vbox_left)
        sizer.Add(panel_left, 0, flag=wx.EXPAND)
        
        code_html = self.__code_html = wx.html.HtmlWindow(self)
        sizer.Add(code_html, 1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        
        
    def on_char(self, evt):
        html_code = self.__code_text.GetValue()
        self.__code_html.SetPage(html_code)
        
        
    def on_clear_click(self, evt):
        self.__code_text.SetValue('')
        
        

class App(wx.App):
    def OnInit(self):
        frame = CodeFrame(parent=None)
        frame.Show()
        return True
        
    
if __name__ == '__main__':
    app = App()
    app.MainLoop()