@echo off

rem the path of the wsclipb.bat is 
rem   wavesynlib\gadgets\wsclipb.bat

rem the path of the wsvimbufp.py is
rem   wavesynlib\gadgets\wsvimbufp.py

%~dp0\wsvimbufp --gvim --tempext=htm | %~dp0\wsclipb -w --html