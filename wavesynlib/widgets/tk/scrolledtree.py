from __future__ import annotations

from tkinter import Frame, Tk
from tkinter.ttk import Scrollbar, Treeview

from toolz import first, second

from wavesynlib.languagecenter.utils import FunctionChain, MethodDelegator


class ScrolledTree(Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pack(expand="yes", fill="both")
        self._make_widgets()
        self.__on_item_double_click = FunctionChain()

        def on_double_click(event):
            item_id = self.tree.identify("item", event.x, event.y)
            item_properties = self.tree.item(item_id)
            return self.__on_item_double_click(item_id, item_properties)
        self.tree.bind("<Double-1>", on_double_click)

    def clear(self) -> None:
        for child in self.tree.get_children():
            self.tree.delete(child)

    def hide_icon_column(self) -> None:
        self.tree["show"] = "headings"

    @property
    def on_item_double_click(self) -> FunctionChain:
        return self.__on_item_double_click

    def load_dataframe(self, dataframe) -> None:
        self.clear()
        self.tree["columns"] = tuple(dataframe.columns)
        for colname in dataframe.columns:
            self.heading(colname, text=colname)
        for row in dataframe.iterrows():
            self.insert("", "end", text=first(row), values=tuple(second(row)))

    def _make_widgets(self):
        sbar = Scrollbar(self)
        tree = Treeview(self)
        sbar.config(command=tree.yview)
        tree.config(yscrollcommand=sbar.set)
        sbar.pack(side="right", fill="y")
        tree.pack(side="left", expand="yes", fill="both")
        self.tree = tree

    for __method_name in ("bind", "insert", "delete", "heading",
        "selection", "item"):
        locals()[__method_name] = MethodDelegator("tree", __method_name)


if __name__ == "__main__":
    from pandas import DataFrame
    df = DataFrame(data=[[1, 2], [3, 4]], index=["row1", "row2"],
        columns=["col1", "col2"])
    root = Tk()
    st = ScrolledTree(root)
    st.pack()
    st.load_dataframe(df)
    root.mainloop()