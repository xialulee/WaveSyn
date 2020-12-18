# Modelnode for WSSh
#
# Run ls:
# #M! ls
#
# Run ls and store the stdout and stderr in the returned dict (s for storage):
# #M!s ls
#
# Run notepad in new thread, and the thread object is returned (the thread object can be accessed through variable "_").
# #M!t notepad
#
# Assign the return value to variable "retobj"
# #M!|retobj= ls
#
# Store stdout & stderr and assign the returned dict to "retobj"
# #M!s|retobj= ls
#
# Using format string:
# should print 100
# a = 100
# #M!f printf "%s" {a}
# 
# Using quotes
# a = "123 456"
# #M!f printf "%s" "{a}"
# (should print "123 456")
# #M!f printf "%s" {a}
# (should print "123")
#
# Command substitution
# #M!t gvim $(which test.py)
#
# Use Environ var and Command substitution in strings:
# #M! printf "%s" "--$(which python)--"
# #M! printf "%s" "---- $(which $(echo python)) ----"
# #M! printf "%s" "--$PATH--"
# Use $$ as escape of $:
# #M! printf "%s" "$$(which python)"
# (SHould print "$(which python)")



import hy
from .hymodelnode import WSSh
