@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\windows\cmdutils
rem The directory of clipb.py:
rem   wavesynlib\interfaces\windows\clipboard

if "%1"=="--help" (
  echo Convert HTML code in clipboard into formatted text in CF_HTML.
) else (
  %~dp0\..\clipboard\clipb.py -r -e@ | %~dp0\..\clipboard\clipb.py -w -d@ --html
)