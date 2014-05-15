WaveSyn
=======

WaveSyn is a platform for testing and evaluating radar waveform synthesis algorithms originally used by Dr. Yi-nan Zhao's [(orcid)](http://orcid.org/0000-0002-7335-8164) research team. This team is dedicated to developing advanced radar signal processing techniques including adaptive detector and adaptive waveform design methods. The main author of WaveSyn is Feng-cong Li [(orcid)](http://orcid.org/0000-0002-3337-2578).

Pattern synthesis for MIMO radars
-------
This work is based on the theory provided in [Waveform Synthesis for Diversity-Based Transmit Beampattern Design](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?tp=&arnumber=4524058&queryText%3D%E2%80%9CWaveform+synthesis+for+diversity-basedtransmit+beampattern+design%2C). For co-located MIMO radars, to synthesize a beampattern which is close to an ideal beampattern, one should synthesize a correlation matrix <strong>R</strong> at first. This application can help the users to generate an optimized correlation matrix based on a given ideal beampattern. 
![](https://github.com/xialulee/WaveSyn/raw/master/doc/images/PatternFitting-Snapshot.png "PatternFitting window of WaveSyn")<br/>
As shown above, one can simply enter the parameters of the ideal pattern, and after click the "solve" button, the application will solve the semidefinite quadratic programming problem behind the scene. The users can export the generated correlation matrix as Matlab .mat data file or Excel data sheet. The code used in WaveSyn for solving the optimization problem is originally written by Tao Zhang who is a work mate of Feng-cong Li.

Waveform synthesis for SISO and MIMO radars
-------
Though this functionalities have already been implemented, they still have some problems for general usage. Thus we did not publish the corresponding source code. We will upload the code the first time we solved the problems. 

Features of WaveSyn
-------
WaveSyn have some features to make your work easier. These features includes a multimedia console, a help system which is very helpful, and a scripting system which can prevent you from clicking the mouse and stroking the keyboard thousands of times.
###The multimedia console of WaveSyn
The console window is the first window appears on the screen after WaveSyn is launched. This console displays all of the meaningful messages including stdout, stderr, command history, error messages, and embedded multimedia help & information.
![](https://github.com/xialulee/WaveSyn/raw/master/doc/images/Features-Console-Snapshot1.PNG "Console window of WaveSyn")<br/>
![](https://github.com/xialulee/WaveSyn/raw/master/doc/images/Features-Console-Snapshot2.PNG "Console window of WaveSyn")<br/>

###The scripting system
The scripting system helps users to automate WaveSyn. To help users write their own script, WaveSyn is obliging and prints the corresponding commands in the console for most GUI operations, and these printed commands can help users to figure out the object model of WaveSyn. <br/>
Users can enter a piece of code directly in the console window, shown as follows.
![](https://github.com/xialulee/WaveSyn/raw/master/doc/images/Features-Scripting-Snapshot1.png "Console window of WaveSyn")<br/>
The scripting system also supports single tab text editor such as notepad.exe (default on Windows) and Vim (GVim).<br/>
[Learn more about the scripting system.](https://github.com/xialulee/WaveSyn/blob/master/doc/ScriptingIntroduction.md)
