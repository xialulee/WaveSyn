# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:45:33 2014

@author: Feng-cong Li
"""
from __future__ import print_function, division

from numpy import *
from Tkinter import *
from ttk import *

import guicomponents
from guicomponents import Group, ParamItem
from application import Application
from basewindow import FigureWindow
from common import setMultiAttr

import threading


from algorithms import isaa

class SingleWindow(FigureWindow):
#########################Optimize Group############################
    class OptimizeGroup(Group):
        def __init__(self, *args, **kwargs):
            self._app = Application.instance    
            self.__topwin = kwargs.pop('topwin')
            Group.__init__(self, *args, **kwargs)
            self.__num = ParamItem(self)
            self.__num.label.config(text='num')
            self.__num.entryText = '1'
            self.__num.entry.bind('<Return>', lambda event: self.onSolveClick())
            self.__num.checkFunc = self._app.checkInt
            self.__num.pack()
            self.__progress = IntVar()
            self.__finishedwav = IntVar()
            progfrm = Frame(self)
            progfrm.pack()
            self.__progbar = Progressbar(progfrm, orient='horizontal', variable=self.__progress, maximum=100)
            self.__progbar.pack(side=LEFT)
            self.__finishedwavbar = Progressbar(progfrm, orient='horizontal', variable=self.__finishedwav, length=70)
            self.__finishedwavbar.pack(side=RIGHT)
            self.__genbtn = Button(self, text='Generate', command=self.onSolveClick)
            self.__genbtn.pack(side=LEFT)
            Button(self, text='Stop', command=self.onStopBtnClick).pack(side=RIGHT)
            self.name = 'Generate'
            self.algo = isaa.diac
            self.getparams = None
            self.__stopflag = False
    
        def onSolveClick(self):
            tbicon = self._app.tbicon
            self.__stopflag = False
            wavnum = self.__num.getInt()
            progress = [0]
            waveform = [0]
            def exitcheck(k, K, y, y_last):                
                progress[0] = int(k / K * 100)
            self.algo.exitcond['func'] = exitcheck
            self.algo.exitcond['interval'] = 1
            params = self.__topwin.grpParams.getParams()
    
            class AlgoThread(threading.Thread):
                def __init__(self, algo, params, waveform, progress):
                    self.algo = algo
                    self.progress = progress
                    threading.Thread.__init__(self)
                def run(self):
                    waveform[0] = self.algo(**params)
    
            self.__finishedwavbar['maximum'] = wavnum
            for cnt in range(wavnum):
                algothread = AlgoThread(self.algo, params, waveform, progress)
                algothread.start()
                while algothread.isAlive():
                    self.__progress.set(progress[0])
                    tbicon.progress = int((cnt*100+progress[0])/(wavnum*100)*100)
                    self.__topwin.update()
                    if self.__stopflag:
                        break
    ## time.sleep(0.1)
                self.__progress.set(0)
                if self.__stopflag:
                    break
                self.__topwin.figureBook.plot(waveform[0])
                self.__finishedwav.set(cnt+1)
            self.__finishedwav.set(0)
            tbicon.state = guicomponents.TBPF_NOPROGRESS
    
        def onStopBtnClick(self):
            self.__stopflag = True
################################################################    
    class ParamsGroup(Group):
        def __init__(self, *args, **kwargs):
            self._app = Application.instance
            self.__topwin   = kwargs.pop('topwin')
            self.balloon    = self._app.balloon
    
            Group.__init__(self, *args, **kwargs)
            self.__algo = None
            self.__MAXROW = 3
            self.__params = {}            
            self.name = 'Parameters'
    
        @property
        def algo(self):
            return self.__algo
    
        @algo.setter
        def algo(self, algorithm):
            #To do: when algo is reset, the frm should be removed
            frm = Frame(self)
            frm.pack()
            params = algorithm.meta.params
            for idx, name in enumerate(params):
                param = params[name]
                paramitem = ParamItem(frm)
                paramitem.labelText = name
                paramitem.label['width'] = 5
                paramitem.entry['width'] = 8
                if self.balloon:
                    self.balloon.bind_widget(paramitem.label, balloonmsg=param.shortdesc)
                if param.type == 'int':
                    paramitem.checkFunc = self._app.checkInt
                elif param.type == 'float':
                    paramitem.checkFunc = checkFloat
                paramitem.grid(row=idx%self.__MAXROW, column=idx//self.__MAXROW)
                self.__params[param.name] = {'gui':paramitem, 'meta':param}
            self.__algo = algorithm
    
        def getParams(self):
            params = self.__params
            convert = {'int':int, 'float':float, 'expression':eval, '':lambda x: x}
            return {name: convert[params[name]['meta'].type](params[name]['gui'].entryText) for name in params}    
#########################Algorithm Selection Group########################    
    class AlgoSelGroup(Group):
        def __init__(self, *args, **kwargs):
            self._topwin  = kwargs.pop('topwin')
            Group.__init__(self, *args, **kwargs)
            self.__algolist = Combobox(self, value=['ISAA-DIAC'], takefocus=1, stat='readonly', width=12)
            self.__algolist.current(0)
            self.__algolist.pack()
            self.name = 'Algorithms'    
#################################################################
    
    windowName  = 'WaveSyn-SingleSyn'        
    def __init__(self, *args, **kwargs):        
        FigureWindow.__init__(self, *args, **kwargs)
        # The toolbar
        toolTabs    = self.toolTabs
        figureBook  = self.figureBook
        
        frmAlgo = Frame(toolTabs)
        grpAlgoSel  = self.AlgoSelGroup(frmAlgo, topwin=self)
        grpAlgoSel.pack(side=LEFT, fill=Y)
        
        grpParams   = self.ParamsGroup(frmAlgo, topwin=self)
        grpParams.pack(side=LEFT, fill=Y)
        grpParams.algo  = isaa.diac
        
        grpSolve    = self.OptimizeGroup(frmAlgo, topwin=self)
        grpSolve.pack(side=LEFT, fill=Y)
        toolTabs.add(frmAlgo, text='Algorithm')
        
        with self.attributeLock:
            setMultiAttr(self,
                grpAlgoSel  = grpAlgoSel,
                grpParams   = grpParams,
                grpSolve    = grpSolve                         
            )
        

        
        self.makeViewTab()
        # End toolbar
        figureBook.makeFigures(
            figureMeta  = [
                dict(name='Envelope',           polar=False),
                dict(name='Phase',              polar=False),
                dict(name='AutoCorrelation',    polar=False),
                dict(name='PSD',                polar=False)
            ]
        )
        
        figEnvelope = figureBook[0]
        figEnvelope.plotFunction  = lambda samples, *args, **kwargs:\
            figEnvelope.plot(abs(samples), *args, **kwargs)
        
        figPhase    = figureBook[1]
        figPhase.plotFunction   = lambda samples, *args, **kwargs:\
            figPhase.plot(angle(samples), *args, **kwargs)
            
        figAuto     = figureBook[2]
        figAuto.plotFunction    = lambda samples, *args, **kwargs:\
            isaa.plot_acdb(figAuto, samples, *args, **kwargs)
            
        figPSD      = figureBook[3]
        figPSD.plotFunction     = lambda samples, *args, **kwargs:\
            figPSD.plot(abs(fft.fft(samples)), *args, **kwargs)