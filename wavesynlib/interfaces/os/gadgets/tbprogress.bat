@for /f %%h in ('%~dp0\windowselector.py --handle') do %~dp0\progressbarreader.py %%h
