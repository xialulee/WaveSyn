from importlib import import_module
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.languagecenter.python.utils import get_module_path


class _ModelTreeMonitor(Observable):
    def __init__(self):
        super().__init__()

    def _on_add_node(self, node):
        return self.notify_observers(node, 'add')

    def _on_remove_node(self, node):
        return self.notify_observers(node, 'remove')


model_tree_monitor = _ModelTreeMonitor()


class AttributeLock:

    def __init__(self, node):
        super().__init__()
        if not isinstance(node, ModelNode):
            raise TypeError('Only the instance of ModelNode is accepted.')
        self.node = node

    def __enter__(self):
        self.node.attribute_auto_lock = True
        return self.node

    def __exit__(self, *dumb):
        self.node.attribute_auto_lock = False


class ModelNode:
    _xmlrpcexport_ = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        node_name = kwargs.get('node_name', '')
        is_root = kwargs.get('is_root', False)
        is_lazy = kwargs.get('is_lazy', False)
        if not hasattr(self, "_attribute_lock"): 
            object.__setattr__(self, "_attribute_lock", set())
        self.parent_node = None
        self.__root_node = None
        self.__node_path = None
        self.__hy_node_path = None
        self.__is_root = is_root
        self.__is_lazy = is_lazy
        if is_lazy:
            self.__module_name = kwargs.pop('module_name', None)
            self.__class_name = kwargs.pop('class_name', None)
            self.__class_object = kwargs.pop('class_object', None)
            self.__init_args = kwargs.pop('init_args', [])
            self.__init_kwargs = kwargs.pop('init_kwargs', {})
        self.node_name = node_name

    def lock_attribute(self, attribute_name, lock=True):
        """Lock a specified attribute, i.e. the attribute cannot be re-assigned.
For example:        
node.a = 0
node.lock_attribute('a')
If you try to give node.a a new value
node.a = 1
then an AttributeError will be raised."""
        if lock:
            self._attribute_lock.add(attribute_name)
        else:
            if attribute_name in self._attribute_lock:
                self._attribute_lock.remove(attribute_name)

    @property
    def attribute_lock(self):
        """This attribute is in fact a context manager.
If the following statements are executed:
with node.attribute_lock:
  node.a = 0
then node will have a property named 'a', which cannot be re-assigned."""
        return AttributeLock(self)

    def on_connect(self):
        pass

    def __getattribute__(self, attribute_name):
        attr = object.__getattribute__(self, attribute_name)
        if isinstance(attr, ModelNode) and attr.is_lazy:
            self.lock_attribute(attribute_name, lock=False)
            attr = attr.real_node
            with self.attribute_lock:
                setattr(self, attribute_name, attr)
        return attr

    def __setattr__(self, key, val):
        if "_attribute_lock" not in self.__dict__:
            object.__setattr__(self, "_attribute_lock", set())
        if "attribute_auto_lock" not in self.__dict__:
            object.__setattr__(self, "attribute_auto_lock", False)
        if key in self._attribute_lock:
            raise AttributeError(f'Attribute "{key}" is unchangeable.')
        if isinstance(val, ModelNode) and not val.is_root and val.parent_node is None:
            val.node_name = val.node_name if val.node_name else key
            object.__setattr__(val, 'parent_node', self)
            val.lock_attribute('parent_node')
            self.lock_attribute(key)
            model_tree_monitor._on_add_node(val)
        object.__setattr__(self, key, val)
        if self.attribute_auto_lock and key != 'attribute_auto_lock':
            self.lock_attribute(key) 
        if isinstance(val, ModelNode):
            return val.on_connect() 

    @property
    def is_root(self):
        return self.__is_root

    @property
    def is_lazy(self):
        return self.__is_lazy

    @property
    def real_node(self):
        """Initialize and return the real node of a lazy node."""
        node = self
        if self.is_lazy:
            if self.__class_object is None:
                mod = import_module(self.__module_name)
                node = getattr(mod, self.__class_name)(*self.__init_args,
                    **self.__init_kwargs)
            else:
                node = self.__class_object(*self.__init_args, **self.
                    __init_kwargs)
        return node

    def _make_child_path(self, child):
        return f'{self.node_path}.{child.node_name}'

    def _hy_make_child_path(self, child):
        return f'{self.hy_node_path[0:-1:None]} {child.node_name})'

    @property
    def node_path(self):
        if self.__node_path is None:
            if self.is_root:
                self.__node_path = self.node_name
            else:
                self.__node_path = self.parent_node._make_child_path(self)
        return self.__node_path

    @property
    def hy_node_path(self):
        if self.__hy_node_path is None:
            if self.is_root:
                self.__hy_node_path = f'(. {self.node_name})'
            else:
                self.__hy_node_path = self.parent_node._hy_make_child_path(self)
        return self.__hy_node_path

    @property
    def child_nodes(self):
        result = {}
        for attribute_name, attribute in self.__dict__.items():
            if isinstance(attribute, ModelNode) and attribute_name != "parent_node":
                result[attribute_name] = attribute.node_path
        return result

    @property
    def root_node(self):
        if self.__root_node is None:
            node = self
            while True:
                if node.is_root:
                    self.__root_node = node
                    break
                node = node.parent_node
        return self.__root_node

    @property
    def module_path(self):
        return get_module_path(self)

    def add_lazy_local_node(self, node_name, module_name, class_name):
        return setattr(
            self, 
            node_name, 
            ModelNode(
                is_lazy = True, 
                module_name = self.module_path.parent / module_name, 
                class_name = class_name) )


class NodeContainer(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _make_child_path(self, child):
        raise NotImplementedError(
            'Subclass of NodeContainer should implement _make_child_path')

    def _hy_make_child_path(self, child):
        raise NotImplementedError(
            'Subclass of NodeContainer should implement _hy_make_child_path')


class Dict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__()


class NodeDict(NodeContainer, Dict):
    _xmlrpcexport_ = []

    def __init__(self, node_name=''):
        super().__init__(node_name=node_name)

    def _make_child_path(self, child):
        return f'{self.node_path}[{id(child)}]'

    def _hy_make_child_path(self, child):
        return f'{self.hy_node_path[0:-1:None]} [{id(child)}])'

    def __setitem__(self, key, child):
        with child.attribute_lock:
            child.parent_node = self
        model_tree_monitor._on_add_node(child)
        Dict.__setitem__(self, key, child)
        return child.on_connect()

    def __delitem__(self, key):
        model_tree_monitor._on_remove_node(self[key])
        return Dict.__delitem__(self, key)

    def pop(self, key):
        model_tree_monitor._on_remove_node(self[key])
        return Dict.pop(self, key)


class Constant:
    """Constant type of wavesynscript."""
    __slots__ = '__name', '__value', '__doc'
    __cache = {}

    def __new__(cls, name, value=None, doc=None):
        if name in cls.__cache:
            c = cls.__cache[name]
            if value != c.value:
                raise ValueError( 'This constant has already been initialized with a different value.')
        else:
            c = object.__new__(cls)
        return c

    def __init__(self, name, value=None, doc=None):
        if not name in self.__cache:
            self.__name = name
            self.__value = value
            self.__doc = doc
            self.__cache[name] = self

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def doc(self):
        return self.__doc

    def help(self):
        return print(self.doc)


class Constants:
    __name_value_pairs = ('KEYSYM_MODIFIERS', {'Alt_L', 'Alt_R',
        'Control_L', 'Control_R', 'Shift_L', 'Shift_R'}), ('KEYSYM_CURSORKEYS',
        {'KP_Prior', 'KP_Next', 'KP_Home', 'KP_End', 'KP_Left', 'KP_Right',
        'KP_Up', 'KP_Down', 'Left', 'Right', 'Up', 'Down', 'Home', 'End',
        'Next', 'Prior'})
    for [name, value] in __name_value_pairs:
        locals()[name] = Constant(name, value)

    @classmethod
    def append_new_constant(cls, name, value=None, doc=None):
        return setattr(cls, name, Constant(name, value, doc))
