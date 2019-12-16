import re
from wavesynlib.languagecenter.wavesynscript import ModelNode
from .pattern import detect_q3str



class InteractiveShell(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__buffer = []
        self.__prev_line_continuation = False
        self.__in_q3_str = None


    def feed(self, code):
        def do_nothing():
            pass
        wavesynscript = self.parent_node
        buffer = self.__buffer
        block_finished = False
        stripped_code = code.strip()
        if not stripped_code:
            # A blank line ends a block.
            wavesynscript._translate_buffer(buffer)
            code = "\n".join(buffer)
            del buffer[:]
            block_finished = True
        stripped_code = code.strip()
        if not stripped_code:
            # Nothing meaningful input.
            return "EXECUTE", do_nothing
        first_sym, last_sym = stripped_code[0], stripped_code[-1]
        # To-Do: use ":=" in elif clause when updated to Python 3.8.
        match_q3, pattern = detect_q3str(code)[:2]
        if self.__in_q3_str:
            # A q3 (''' or """) string is started before and not closed yet.
            buffer[-1] = f"{buffer[-1]}\n{code}"
            match = re.search(self.__in_q3_str, buffer[-1])
            if match and match["closed"]:
                self.__in_q3_str = None
            return "APPEND", do_nothing
        elif match_q3 and not match_q3['closed']:
            # The current line started a not-closed q3 string.
            self.__in_q3_str = pattern
            buffer.append(code)
            return "APPEND", do_nothing
        elif buffer or \
                    last_sym in (":", "\\") or \
                    (first_sym in ("@",) and not block_finished):
            # A new block, decorated func/class and multiline being created.
            # Store the lines of code in self.__code_list,
            # until a blank line appears.
            code = wavesynscript._remove_line_continuation(code)[0]
            # Remove the line continuation if it exists.
            # We can still know wheter line continuation exists in the original code
            # by reading the last_sym variable.
            if self.__prev_line_continuation:
                # The previous line ends up with a line continuation.
                # Join the current line with the previous line, instead of
                # making a new line.
                buffer[-1] = f"{buffer[-1]}{code}"
            else:
                buffer.append(code)
            self.__prev_line_continuation = last_sym == "\\"
            return "APPEND", do_nothing
        else:
            # One-line code
            def execute():
                nonlocal code
                try:
                    code = wavesynscript.extra_modes.translate(code, verbose=True)[0]
                except SyntaxError:
                    pass
                return wavesynscript.execute(code)
            return "EXECUTE", execute