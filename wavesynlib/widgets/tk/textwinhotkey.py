from tkinter import Text



class TextWinHotkey(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.bind('<Control-Key-a>', lambda event: self.select_all())
        self.bind('<Control-Key-c>', lambda event: 0)

    def select_all(self):
        self.tag_add('sel', '1.0', 'end-1c')
        self.see('insert')
        self.focus()
        return 'break'
