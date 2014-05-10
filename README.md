WaveSyn
=======

WaveSyn is a platform for testing and evaluating radar waveform synthesis algorithms originally used by Dr. Yi-nan Zhao's [(orcid)](http://orcid.org/0000-0002-7335-8164) research team. This team is dedicated to developing advanced radar signal processing techniques including adaptive detector and adaptive waveform design methods. The main author of WaveSyn is Feng-cong Li [(orcid)](http://orcid.org/0000-0002-3337-2578).

Pattern synthesis for MIMO radars
-------
This work is based on the theory provided in [Waveform Synthesis for Diversity-Based Transmit Beampattern Design](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?tp=&arnumber=4524058&queryText%3D%E2%80%9CWaveform+synthesis+for+diversity-basedtransmit+beampattern+design%2C). For co-located MIMO radars, to synthesize a beampattern which is close to an ideal beampattern, one should synthesize a correlation matrix R at first. This application can help the users to generate a optimized correlation matrix based on a given ideal beampattern. 
![github](https://github.com/xialulee/WaveSyn/blob/1b7866c7df1dfcb73dea6376d118990d58116ad2/doc/PatternFitting-Snapshot.png "github")
As shown above, one can simply enter the parameters of the ideal pattern, and after click the "solve" button, the application will solve the semidefinite quadratic programming problem behind the scene. The users can export the generated correlation matrix as Matlab .mat data file or Excel data sheet. 

Waveform synthesis for SISO and MIMO radars
-------
Though this functionalities have already been implemented, they still have some problems for general usage. Thus we did not publish the corresponding source code. We will upload the code the first time we solved the problems. 
