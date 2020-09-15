from pathlib import Path



def winpath_to_wslpath(path):
    if str(path).startswith(r"\\wsl$"):
        result = Path("/")
    else:
        result = Path("/mnt")
        result /= path.drive[:-1].lower()
    for part in path.parts[1:]:
        result /= part.lower()
    return result
