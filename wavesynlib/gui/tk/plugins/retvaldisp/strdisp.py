"""
Created on March 29 15:56 2023

@author: F. C. Li
"""

from . import BasePlugin


class Plugin(BasePlugin):
    """\
A plugin for returning string values. It generates a "Copy" link when the return value is of type str, allowing the content of the return value to be copied to the clipboard. 
"""
    _type = str
    
    def action(self, data):
        if not self.test_data(data):
            return
        
        self.root_node.gui.console.show_tips([{
            "type": "link",
            "content": "Copy",
            "command": lambda *args: self.root_node.interfaces.os.clipboard.write(data)
        }])
