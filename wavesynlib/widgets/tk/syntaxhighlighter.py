from wavesynlib.languagecenter.python.pattern import prog as prog_pattern
    


class SyntaxHighlighter:
    def __init__(self, text_widget, syntax_tags):
        self.__text_widget = text_widget
        self.__syntax_tags = syntax_tags
        
    
    def highlight_one_row(self, row):
        text = self.__text_widget
        
        for tag in self.__syntax_tags:
            text.tag_remove(tag, f'{row}.0', f'{row}.end')
            
        line = text.get(f'{row}.0', f'{row}.end')
        start = 0
        while True: 
            m = prog_pattern.search(line, start)
            if not m: 
                break
            start = m.end()
            for key, value in m.groupdict().items():
                if value:
                    text.tag_add(
                        key, 
                        f'{row}.{m.start()}',
                        f'{row}.{m.end()}')        
        
        
                        