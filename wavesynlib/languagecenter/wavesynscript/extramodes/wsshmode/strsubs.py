import regex


SUBS_NORMAL_STR = r"""
(?:
    [^$\\\)\n;|&]*
    (?:
        \\.      # A escaped char
        [^$\\\)\n;|&]*
    )*
)
"""

# Should be \$[_a-zA-Z]\w*
# But sometimes type env var wrong
# If not match, no error message pop out. 
SUBS_ENVVAR_STR = r"(?P<SUBS_ENVVAR>\$\w+)"

SUBS_STR_OR_VAR_STR = rf"""
(?:
    {SUBS_NORMAL_STR}
    | #or
    {SUBS_ENVVAR_STR}
)
"""

#SUBS_COMMAND_STR = rf"""
#(?P<SUBS_COMMAND>
#    \$\(  # Command substitution starts with $(
#    {SUBS_STR_OR_VAR_STR}*
#    (?:
#        (?R)  # Nested command substitution.
#        {SUBS_STR_OR_VAR_STR}
#    )*
#    \)  # Command substitution ends with )
#)
#"""

SUBS_COMMAND_STR = rf"""
(?P<SUBS_COMMAND>
    \$\(  # Command substitution starts with $(
    (?:
        (?R)?  # Nested command substitution.
        {SUBS_STR_OR_VAR_STR}?
    )*
    \)  # Command substitution ends with )
)
"""
SUBS_COMMAND = regex.compile(SUBS_COMMAND_STR, regex.VERBOSE)
SUBS_ENV_VAR = regex.compile(SUBS_ENVVAR_STR, regex.VERBOSE)
SUBS_NORMAL  = regex.compile(SUBS_NORMAL_STR, regex.VERBOSE)
