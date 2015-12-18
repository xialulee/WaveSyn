@echo off

rem Get the selected window's corresponding PID, and print the startup parameters of the process.

if "%1" == "--help" (
  echo Get the startup parameters of the selected window's process.
) else (
  for /f %%p in ('%~dp0\windowselector.py --pid') do %~dp0\procparam.py --pid=%%p
)