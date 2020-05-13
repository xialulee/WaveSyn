from datetime import date
from wavesynlib.widgets.tk import monthcalendar



class Plugin:
    _type = date


    def __init__(self, root_node):
        self.__root = root_node


    def test_data(self, data):
        if isinstance(data, self._type):
            return True
        else:
            return False


    def action(self, data):
        if not self.test_data(data):
            return
        self.__root.gui.console.show_tips([{
            "type": "link",
            "content": "Show month calendar.",
            "command": lambda *args: monthcalendar.show_date(data) }])