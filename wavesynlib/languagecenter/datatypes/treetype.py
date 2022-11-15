from abc import ABC, abstractmethod



class AbstractTreeNode(ABC):
    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def is_group(self):
        pass

    @abstractmethod
    def make_group(self, group_info):
        pass

    @abstractmethod
    def make_leaf(self, leaf_info):
        pass


def tree_trans(source, dest):
    for item in source:
        if item.is_group():
            tree_trans(item, dest.make_group(item))
        else:
            dest.make_leaf(item)
