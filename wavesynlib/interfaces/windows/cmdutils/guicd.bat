@rem The directory of this bat file:
@rem   wavesynlib\interfaces\windows\cmdutils
@rem The directory of pathselector.py:
@rem   wavesynlib\guicomponents\

@for /f %%h in ('%~dp0\..\..\..\guicomponents\pathselector.py --dir') do @cd /d %%h