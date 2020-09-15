from pathlib import Path



def winpath_to_wslpath(path):
    result = Path("/mnt")
    result /= path.drive[:-1].lower()
    for part in path.parts[1:]:
        result /= part.lower()
    return result
