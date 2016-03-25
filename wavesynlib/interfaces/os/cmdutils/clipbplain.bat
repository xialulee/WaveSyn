@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\windows\cmdutils
rem The directory of clipb.py:
rem   wavesynlib\interfaces\windows\clipboard

if "%1"=="--help" (
  echo Convert formatted text in clipboard into plain text.
) else (
  %~dp0\..\clipboard\clipb.py -r -e@ | %~dp0\..\clipboard\clipb.py -w -d@
)