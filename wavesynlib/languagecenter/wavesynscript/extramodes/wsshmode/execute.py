
import io
import sys
import locale
codename = locale.getpreferredencoding()
import pathlib
from subprocess import Popen, PIPE

from wavesynlib.gadgets import wswhich

from .parse import split, group



def _substitute(cmd):
    for index in range(len(cmd)):
        token = cmd[index]
        if isinstance(token, list) and token[0]=="$":
            stdout = io.StringIO()
            run(group(token[1:]), stdout=stdout)
            stdout.seek(0)
            text = stdout.read().rstrip()
            cmd[index] = text
            

            
def _win_exe_expr(cmd):
    try:
        path = wswhich.which(cmd[0])[0]
    except IndexError:
        path = pathlib.Path(cmd[0])
    if path.suffix.lower() == ".exe":
        expr = cmd
    elif path.suffix.lower() == ".py":
        expr = ["python", str(path), *cmd[1:]]
    else:
        expr = cmd
    return expr



def run(command, stdout=None, stderr=None):
    STDOUT = stdout if stdout else sys.stdout
    STDERR = stderr if stderr else sys.stderr
    
    if isinstance(command, str):
        cmd_tokens = split(command)
        cmd_groups = group(cmd_tokens)
    elif isinstance(command, list):
        cmd_groups = command
    else:
        raise TypeError("Type of command not supported.")
        
    proc_list = []
    outerrpipe = {"stdout":PIPE, "stderr":PIPE, "encoding":codename}
        
    for index, cmd in enumerate(cmd_groups):
        op = cmd[0]
        cmd = cmd[1:]
        
        _substitute(cmd)
        cmd = _win_exe_expr(cmd) 
        
        if op == "":
            proc = Popen(cmd, **outerrpipe)
        elif op == "|":
            prev_proc = proc_list[index-1]
            proc = Popen(cmd, stdin=prev_proc.stdout, **outerrpipe)
            prev_proc.poll()
            prev_proc.stdout.close()
            errmsg = prev_proc.stderr.read()
            prev_proc.stderr.close()
            if errmsg:
                print(f"{cmd_groups[index-1][1:]}:\n{errmsg}", file=STDERR)
        else:
            raise ValueError(f"Operator {op} not supported.")
        proc_list.append(proc)
    last_proc = proc_list[-1]
    out, err = last_proc.communicate()
    print(out, file=STDOUT)
    if err:
        print(f"{cmd_groups[-1][1:]}:\n{err}", file=STDERR)
    return last_proc.returncode
            
            