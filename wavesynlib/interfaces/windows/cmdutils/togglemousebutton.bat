@echo off

rem The directory of this bat file:
rem   wavesynlib\interfaces\windows\cmdutils\
rem The directory of pyrundll.py:
rem   wavesynlib\interfaces\windows\cmdutils\

setlocal
if "%1"=="--help" (
	echo If mouse buttons are swapped, then restore; if not, then swap.
) else (
	for /f %%r in ('%~dp0\rundll.py user32 GetSystemMetrics SM_SWAPBUTTON:WIN32CONST') do (
		if %%r == 1 (
			%~dp0\restoremousebutton.bat
		) else (
			%~dp0\swapmousebutton.bat
		)
	)
)
endlocal