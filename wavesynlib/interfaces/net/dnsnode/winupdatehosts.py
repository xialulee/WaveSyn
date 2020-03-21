import os
import sys
import pickle
from pathlib import Path



def get_hosts_path():
    root = Path(os.environ["SYSTEMROOT"])
    return root / r"System32\drivers\etc\hosts"



def read_file():
    content = []
    with open(get_hosts_path()) as f:
        for line in f:
            sline = line.strip()
            if sline.startswith("#"):
                content.append(["comment", line])
                continue
            if not sline:
                content.append(["blank", line])
                continue
            fields = sline.split(maxsplit=2)
            if len(fields) < 2:
                content.append(["unknown", line])
                continue
            else:
                content.append(["entry", line, fields])
    return content



def make_ip_str(ip):
    return (ip+" "*15)[:15]



def update(data, content):
    content = read_file()
    for line_data in content:
        if line_data[0] in ("comment", "blank", "unknown"):
            continue
        fields = line_data[-1]
        if fields[1] in data:
            ip = data[fields[1]]
            new_line = f"{make_ip_str(ip)} {fields[1]}"
            if len(fields) == 3:
                new_line += f"\t{fields[2]}"
            new_line += "\n"
            line_data[1] = new_line
    return content


def write_file(content):
    with open(get_hosts_path(), "w") as f:
        for line_data in content:
            f.write(line_data[1])


if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, "rb") as f:
        data = pickle.load(f)
    write_file(update(data, read_file()))
    os.remove(path)
