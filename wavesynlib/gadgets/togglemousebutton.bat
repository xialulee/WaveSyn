@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\os\cmdutils\
rem The directory of wsrundll.py:
rem   wavesynlib\interfaces\os\cmdutils\

setlocal
if "%1"=="--help" (
	echo If mouse buttons are swapped, then restore; if not, then swap.
) else (
	for /f %%r in ('%~dp0\wsrundll.py user32 GetSystemMetrics SM_SWAPBUTTON:WIN32CONST') do (
		if %%r == 1 (
			%~dp0\restoremousebutton.bat
		) else (
			%~dp0\swapmousebutton.bat
		)
	)
)
endlocal