from importlib import import_module
from wavesynlib.languagecenter.wavesynscript import NodeDict



class Toolboxes(NodeDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, toolbox_name):
        if toolbox_name in self:
            return super().__getitem__(toolbox_name)
        mod = import_module(
            f'.{toolbox_name}.toolboxnode', '.'.join(
                __name__.split('.')[0:-1:None]
            )
        )
        node = mod.ToolboxNode(toolbox_name=toolbox_name)
        self[toolbox_name] = node
        return node

    def _make_child_path(self, child):
        return f'{self.node_path}[{repr(child._toolbox_name)}]'

    def _hy_make_child_path(self, child):
        return f'{self.hy_node_path[0:-1:None]} [{repr(child._toolbox_name)}])'
