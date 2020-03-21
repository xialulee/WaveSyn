import sys
import pickle
import tempfile
import platform
import pandas
import dns.resolver
from pathlib import Path

from wavesynlib.languagecenter.wavesynscript import ModelNode

_winupdatehosts_path = str(Path(__file__).parent / "winupdatehosts.py")



class HostsFile(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def read(self, format="pandas"):
        path = self.get_path()
        table = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                fields = line.split(maxsplit=2)
                if len(fields) < 2:
                    continue
                fields.append("")
                table.append(fields[:3])
        if format in ("native", "python"):
            return table
        table = pandas.DataFrame(table, columns=("ip", "host", "comment"))
        return table
        

    def edit(self, editor=None):
        system = platform.system()
        if system == "Windows":
            self.root_node.interfaces.os.windows.edit_hosts(editor=editor)
        else:
            raise NotImplementedError("Not implemented on this platform.")


    def get_path(self):
        system = platform.system()
        if system == "Windows":
            return self.root_node.interfaces.os.windows.get_hosts_path()
        else:
            raise NotImplementedError("Not implemented on this platform.")


    def update(self, filter=lambda index, row: True, name_servers=None):
        resolver = dns.resolver.Resolver()
        if name_servers:
            resolver.nameservers = name_servers
        table = self.read()
        ipmap = {}
        for index, row in table.iterrows():
            if not filter(index, row):
                continue
            try:
                ip = resolver.query(row.host)[0].address
            except dns.resolver.NXDOMAIN:
                continue
            ipmap[row.host] = ip
        if platform.system() == "Windows":
            with tempfile.NamedTemporaryFile("wb", delete=False) as tfile:
                pickle.dump(ipmap, tfile)
            self.root_node.interfaces.os.windows.processes.utils.run_as_admin(
                sys.executable, 
                f'"{_winupdatehosts_path}" "{tfile.name}"')

    

class DNS(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.hosts_file = ModelNode(
            is_lazy=True,
            class_object=HostsFile)
