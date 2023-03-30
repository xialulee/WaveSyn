from __future__ import annotations

import os
import re
import io
import sys
import locale
codename = locale.getpreferredencoding()
import pathlib
from subprocess import Popen, PIPE

from wavesynlib.gadgets import wswhich

from .parse import split, group
from .cmdbuiltins import is_cmd_builtin


envvar_prog = re.compile(r"^\$\w+$")



embed_envvar_pat  = r"(?P<EMBED_ENVVAR>\$\w+)"
cmdsubs_start_pat = r"(?P<CMDSUBS_START>\$\()"
cmdsubs_stop_pat  = r"(?P<CMDSUBS_STOP>\))"
normal_str_pat    = r"(?P<NORMAL_STR>[^$]+)"
escape_ds_pat     = r"(?P<ESCAPE_DS>\$\$)"
str_parse_pat     = "|".join((escape_ds_pat, normal_str_pat, embed_envvar_pat, cmdsubs_start_pat, cmdsubs_stop_pat))
str_parse_prog    = re.compile(str_parse_pat)
cmdsubs_parse_prog= re.compile(f"{cmdsubs_start_pat}|{cmdsubs_stop_pat}")

def _format_string(string):
    result = []
    subs_level = 0
    while True:
        match = str_parse_prog.match(string)
        if not match:
            break
        match_str = match.group(0)
        lastgroup = match.lastgroup
        if lastgroup == "NORMAL_STR":
            result.append(match_str)
            string = string[len(match_str):]
        elif lastgroup == "ESCAPE_DS":
            result.append("$")
            string = string[len(match_str):]
        elif lastgroup == "EMBED_ENVVAR":
            result.append(os.environ[match_str[1:]])
            string = string[len(match_str):]
        elif lastgroup == "CMDSUBS_START":
            subs_level = 1
            string = string[len(match_str):]
            cmdsubs_list = []
            search_start = 0
            while subs_level > 0:
                match = cmdsubs_parse_prog.search(string, pos=search_start)
                if not match:
                    raise SyntaxError("Round brackets of command substitution not match.")
                match_str = match.group(0)
                lastgroup = match.lastgroup
                if lastgroup == "CMDSUBS_STOP":
                    subs_level -= 1
                    if subs_level == 0:
                        cmdsubs_list.append(string[:match.start()])
                        string = string[match.end():]
                elif lastgroup == "CMDSUBS_START":
                    subs_level += 1
                search_start = match.end()
            cmdsubs_str = "".join(cmdsubs_list)
            stdout = io.StringIO()
            run(command=cmdsubs_str, stdout=stdout)
            stdout.seek(0)
            result.append(stdout.read().rstrip())
        else:
            raise SyntaxError("Unknown Error.")
    return "".join(result)




def _substitute(cmd, shell=""):
    for index, token in enumerate(cmd):
        if isinstance(token, list) and token[0]=="$":
            # Command substitution. 
            # E.g. #M! dir $(echo c:\lab)
            # cmd == ['dir', ['$', 'echo', 'c:\\lab']]
            # token == ['$', 'echo', 'c:\\lab']
            # Only need to implement substitution for CMD.
            if shell != "cmd":
                cmd[index] = f"$({' '.join(token[1:])})"
            else:
                stdout = io.StringIO()
                run(group(token[1:]), stdout=stdout, shell=shell)
                stdout.seek(0)
                text = stdout.read().rstrip()
                cmd[index] = text
        elif isinstance(token, str) and envvar_prog.match(token):
            if shell == "cmd":
                # CMD cannot ref a env var with $.
                # This is an extenstion to CMD syntax. 
                cmd[index] = os.environ[token[1:]]
        elif "$" in token:
            if shell == "cmd":
                token = _format_string(token)
                cmd[index] = token
            

            
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



def run(
        command: str|list,
        stdin:  str|None = None,
        stdout: io.IOBase|None = None,
        stderr: io.IOBase|None = None,
        shell:  str = ""
    ) -> int:
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
        
        if shell == "wsl":
            cmd = ["wsl", *cmd]
        elif shell == "cmd":
            if is_cmd_builtin(cmd[0]):
                cmd = ["cmd", "/c", *cmd]
        else:
            pass
        
        _substitute(cmd, shell=shell)

        cmd = _win_exe_expr(cmd) 
        
        if op == "":
            if stdin:
                proc = Popen(cmd, stdin=PIPE, **outerrpipe)
                proc.stdin.write(stdin)
                proc.stdin.close()
            else:
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
            
            