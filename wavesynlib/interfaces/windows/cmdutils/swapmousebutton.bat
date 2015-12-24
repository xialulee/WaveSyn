@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\windows\cmdutils\
rem The directory of pyrundll.py:
rem   wavesynlib\interfaces\windows\

if "%1"=="--help" (
  echo Swap Left and Right mouse buttons.
) else (
  %~dp0\..\pyrundll.py user32 SwapMouseButton 1:BOOL
)