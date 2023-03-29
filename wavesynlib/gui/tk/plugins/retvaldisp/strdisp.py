from . import BasePlugin



class Plugin(BasePlugin):
    _type = str
    
    def action(self, data):
        if not self.test_data(data):
            return
        
        self.root_node.gui.console.show_tips([{
            "type": "link",
            "content": "Copy",
            "command": lambda *args: self.root_node.interfaces.os.clipboard.write(data)
        }])
