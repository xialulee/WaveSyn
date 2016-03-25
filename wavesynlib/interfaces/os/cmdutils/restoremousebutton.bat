@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\windows\cmdutils\
rem The directory of pyrundll.py:
rem   wavesynlib\interfaces\windows\cmdutils\

if "%1"=="--help" (
  echo Restore Left and Right mouse buttons settings.
) else (
  %~dp0\rundll.py user32 SwapMouseButton 0:BOOL
)