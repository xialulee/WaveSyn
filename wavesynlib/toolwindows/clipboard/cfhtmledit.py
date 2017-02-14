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
        code_text = self.__code_text = wx.TextCtrl(self, -1, "Input HTML code here.", style=wx.TE_MULTILINE)
        code_text.SetInsertionPoint(0)
        code_text.Bind(wx.EVT_KEY_UP, self.on_char)
        sizer.Add(code_text, 0, flag=wx.EXPAND)
        
        code_html = self.__code_html = wx.html.HtmlWindow(self)
        sizer.Add(code_html, 1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        
        
    def on_char(self, evt):
        html_code = self.__code_text.GetValue()
        self.__code_html.SetPage(html_code)
        
        

class App(wx.App):
    def OnInit(self):
        frame = CodeFrame(parent=None)
        frame.Show()
        return True
        
    
if __name__ == '__main__':
    app = App()
    app.MainLoop()