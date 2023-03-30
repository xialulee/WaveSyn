cmdbuiltins = set((
    'ASSOC',
    'BREAK',
    'CALL',
    'CD',
    'CHDIR',
    'CLS',
    'COLOR',
    'COPY',
    'DATE',
    'DEL',
    'DIR',
    'creates',
    'ECHO',
    'ENDLOCAL',
    'ERASE',
    'EXIT',
    'FOR',
    'FTYPE',
    'GOTO',
    'GRAFTABL',
    'graphics',
    'IF',
    'MD',
    'MKDIR',
    'MKLINK',
    'MOVE',
    'PATH',
    'PAUSE',
    'POPD',
    'PUSHD',
    'PROMPT',
    'PUSHD',
    'RD',
    'REM',
    'REN',
    'RENAME',
    'RMDIR',
    'SET',
    'SETLOCAL',
    'SHIFT',
    'START',
    'TIME',
    'TITLE',
    'TYPE',
    'VER',
    'VERIFY',
    'VOL'
))


def is_cmd_builtin(command: str) -> bool:
    """\
Check a command whether it is a cmd builtin command. 
"""
    return command.upper() in cmdbuiltins
        