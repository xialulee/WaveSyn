from datetime import date
from wavesynlib.widgets.tk import monthcalendar

from . import BasePlugin



class Plugin(BasePlugin):
    _type = date


    def action(self, data):
        if not self.test_data(data):
            return
        self.root_node.gui.console.show_tips([{
            "type": "link",
            "content": "Show month calendar.",
            "command": lambda *args: monthcalendar.show_date(data) }])