from tkinter import Toplevel, Label
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.widgets.tk import ScrolledList



class CandidateList(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def launch(self, completions):
        console_text = self.parent_node
        text_widget = console_text.text

        acw = Toplevel(text_widget)
        acw.wm_overrideredirect(1)
        acw.wm_attributes("-topmost", True)

        seltext = Label(acw, anchor="w", justify="left")
        seltext.pack(expand="yes", fill="x")

        candidates = ScrolledList(acw)
        candidates.pack(expand="yes", fill="both")
        candidates.list_config(selectmode="single")

        x, y = text_widget.bbox("insert")[:2]
        x += text_widget.winfo_rootx()
        y += text_widget.winfo_rooty()
        # y+h is the position below the current line.
        acw.geometry(f"+{x}+{y}")
        candidates.list.focus_set()

        def on_exit(event):
            acw.destroy()

        acw.bind("<FocusOut>", on_exit)
        candidates.list.bind("<Escape>", on_exit)

        def on_updown(event, direction):
            current_sel = int(candidates.current_selection[0])
            new_sel     = current_sel + direction
            if not (0 <= new_sel < candidates.length):
                return "break"
            candidates.selection_clear(current_sel)
            candidates.selection_set(new_sel)
            candidates.see(new_sel)
            return "break"

        candidates.list.bind("<Down>",      lambda event: on_updown(event, +1))
        candidates.list.bind("<Tab>",       lambda event: on_updown(event, +1))
        candidates.list.bind("<Up>",        lambda event: on_updown(event, -1))
        candidates.list.bind("<Shift-Tab>", lambda event: on_updown(event, -1))

        for completion in completions:
            candidates.append(completion.name)

        candidates.selection_set(0)

        def on_select(event):
            current_sel = int(candidates.current_selection[0])
            complete_str = completions[current_sel].complete
            text_widget.insert("end", complete_str)
            on_exit(None)

        candidates.list.bind("<Return>",          on_select)
        candidates.list.bind("<ButtonRelease-1>", on_select)

        keyseq = [""]
        constants = self.root_node.lang_center.wavesynscript.constants

        def on_key_press(event):
            if (event.keysym not in constants.KEYSYM_MODIFIERS.value) and \
                (event.keysym not in constants.KEYSYM_CURSORKEYS.value):
                if event.keysym=='BackSpace':
                    keyseq[0] = keyseq[0][:-1]
                else:
                    keyseq[0] += event.keysym
                seltext['text'] = keyseq[0]
                for index, completion in enumerate(completions):
                    if completion.complete.startswith(keyseq[0]):
                        current_sel = int(candidates.current_selection[0])
                        candidates.selection_clear(current_sel)
                        candidates.selection_set(index)
                        candidates.see(index)
                        return
                on_exit(None)
            else:
                return
        candidates.list.bind('<KeyPress>', on_key_press)
        # No more key bindings hereafter. 