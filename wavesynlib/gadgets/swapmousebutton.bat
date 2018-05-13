@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\os\cmdutils\
rem The directory of pyrundll.py:
rem   wavesynlib\interfaces\os\cmdutils\

if "%1"=="--help" (
  echo Swap Left and Right mouse buttons.
) else (
  %~dp0\wsrundll.py user32 SwapMouseButton 1:BOOL
)