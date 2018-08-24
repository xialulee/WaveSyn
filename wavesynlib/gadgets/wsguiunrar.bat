@echo off

rem The directory of this bat file:
rem   wavesynlib\gadgets.

rem The directory of wspathselector:
rem   wavesynlib\gadgets.

rem The directory of wscmdsubs:
rem   wavesynlib\gadgets.

rem The path of unrar.exe should be in %PATH%.


wscmdsubs unrar x $"%~dp0\wspathselector.py --filetype=*.rar" $"%~dp0\wspathselector.py -d"