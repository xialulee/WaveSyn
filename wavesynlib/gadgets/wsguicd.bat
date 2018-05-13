@rem The directory of this bat file:
@rem   wavesynlib\interfaces\os\cmdutils
@rem The directory of pathselector.py:
@rem   wavesynlib\widgets\

@for /f %%h in ('%~dp0\wspathselector.py --dir') do @cd /d %%h
