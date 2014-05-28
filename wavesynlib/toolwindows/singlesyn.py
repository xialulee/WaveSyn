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
from guicomponents  import Group, ParamItem
from application    import Application, ScriptCode, Scripting
from basewindow     import FigureWindow, askClassName
from common         import setMultiAttr, autoSubs

import threading
import json

from mathtools  import AlgorithmDict, AlgorithmNode
#from algorithms import isaa



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
        #self.algo = isaa.diac
        #self.algo   = self.__topwin.currentAlgorithm
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
        self.algo   = self.__topwin.currentAlgorithm            
        self.algo.exitcond['func'] = exitcheck
        self.algo.exitcond['interval'] = 1
        params = self.__topwin.grpParams.getParams()

        class AlgoThread(threading.Thread):
            def __init__(self, algo, params, waveform, progress):
                self.algo = algo
                self.progress = progress
                threading.Thread.__init__(self)
            def run(self):
                printCode   = True
                #waveform[0] = self.algo.run(**params)
                self.algo.run(**params)
        
#        def waveformSynthesis(**params):
#            printCode   = True
#            self.__topwin.currentData    = self.algo.run(**params)

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
            #self.__topwin.figureBook.plot(waveform[0])
            printCode   = True
            self.__topwin.plotCurrentData()
            self.__finishedwav.set(cnt+1)
        self.__finishedwav.set(0)
        tbicon.state = guicomponents.TBPF_NOPROGRESS

    def onStopBtnClick(self):
        self.__stopflag = True



class ParamsGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin   = kwargs.pop('topwin')
        self.balloon    = self._app.balloon

        Group.__init__(self, *args, **kwargs)
        self.__algo = None
        self.__MAXROW = 3
        self.__params = {}  

        self.__frameDict    = {}
          
        self.name = 'Parameters'

#    @property
#    def algo(self):
#        return self.__algo

#    @algo.setter
    def appendAlgorithm(self, algorithm):
        #To do: when algo is reset, the frm should be removed
        for algoName in self.__frameDict:
            self.__frameDict[algoName]['frame'].pack_forget()
        frm = Frame(self)
        frm.pack()
        paramInfo   = {}
        params = algorithm['parameters']
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
            #self.__params[param.name] = {'gui':paramitem, 'meta':param}
            paramInfo[param.name] = {'gui':paramitem, 'meta':param}
        self.__algo = algorithm
        #self.__frameDict[algorithm.meta.name]   = frm
        self.__frameDict[algorithm['name']]   = dict(frame=frm, paramInfo=paramInfo)
        self.__params   = paramInfo

    def getParams(self):
        params = self.__params
        convert = {'int':int, 'float':float, 'expression':lambda expr: ScriptCode(expr), '':lambda x: x}
        return {name: convert[params[name]['meta'].type](params[name]['gui'].entryText) for name in params}
        
    def changeAlgorithm(self, algorithmName):
        for algoName in self.__frameDict:
            self.__frameDict[algoName]['frame'].pack_forget()        
        self.__frameDict[algorithmName]['frame'].pack()
        self.__params   = self.__frameDict[algorithmName]['paramInfo']
        
        
class AlgoSelGroup(Group):
    def __init__(self, *args, **kwargs):
        self._topwin  = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        
        #self.__algoList = Combobox(self, value=['ISAA-DIAC'], takefocus=1, stat='readonly', width=12)
        self.__algoList = Combobox(self, value=[], takefocus=1, stat='readonly', width=12)
        self.__algoList['values']   = []
        self.__algoList.pack()
        self.__algoList.bind('<<ComboboxSelected>>', self.onAlgorithmChange)
        
        Button(self, text='Load Algorithm', command=self.onLoadAlgorithm).pack()
        
        self.name = 'Algorithms'          
        
    @property
    def algoList(self):
        return self.__algoList
        
    def onAlgorithmChange(self, event):
        self._topwin.grpParams.changeAlgorithm(event.widget.get())
        
    def onLoadAlgorithm(self):
        printCode   = True
        moduleName, className   = askClassName()
        self._topwin.loadAlgorithm(moduleName=moduleName, className=className)


class SingleWindow(FigureWindow):      
    windowName  = 'WaveSyn-SingleSyn'        
    def __init__(self, *args, **kwargs):     
        FigureWindow.__init__(self, *args, **kwargs)
        self.currentData    = None
        
        # algorithm dict and current data
        self.algorithms = AlgorithmDict()
        self.lockAttribute('algorithms')
        #        
        
        # The toolbar
        toolTabs    = self.toolTabs
        figureBook  = self.figureBook
        
        frmAlgo = Frame(toolTabs)
        grpAlgoSel  = AlgoSelGroup(frmAlgo, topwin=self)
        grpAlgoSel.pack(side=LEFT, fill=Y)
        
        grpParams   = ParamsGroup(frmAlgo, topwin=self)
        grpParams.pack(side=LEFT, fill=Y)
        
        grpSolve    = OptimizeGroup(frmAlgo, topwin=self)
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
        
        with open(Application.instance.configFileName) as f:
            config  = json.load(f)
        algorithms  = config['SingleWaveformAlgorithms']

        for algo in algorithms:
            self.loadAlgorithm(moduleName=algo['ModuleName'], className=algo['ClassName'])
#            grpParams.appendAlgorithm(algoNode)
        self.grpAlgoSel.algoList.current(len(algorithms)-1)
        
        figEnvelope = figureBook[0]
        figEnvelope.plotFunction  = lambda samples, *args, **kwargs:\
            figEnvelope.plot(abs(samples), *args, **kwargs)
        
        figPhase    = figureBook[1]
        figPhase.plotFunction   = lambda samples, *args, **kwargs:\
            figPhase.plot(angle(samples), *args, **kwargs)
            
        def plot_acdb(s, *args, **kwargs):
            if not isinstance(s, ndarray):
                s   = array(s)
            N       = len(s)
            ac      = convolve(s, conj(s[::-1]))
            acdb    = 20*log10(abs(ac))
            acdb    = acdb - max(acdb)
            figAuto.plot(r_[(-N+1):N], acdb, *args, **kwargs)            
            
        figAuto     = figureBook[2]
        figAuto.plotFunction    = plot_acdb
            
        figPSD      = figureBook[3]
        figPSD.plotFunction     = lambda samples, *args, **kwargs:\
            figPSD.plot(abs(fft.fft(samples)), *args, **kwargs)
    
    @Scripting.printable        
    def loadAlgorithm(self, moduleName, className):
#        mod     = __import__(autoSubs('algorithms.$moduleName'), globals(), locals(), [className], -1)
#        node    = AlgorithmNode(getattr(mod, className)())
        node    = AlgorithmNode(moduleName, className)
        self.algorithms.add(node)
        values  = self.grpAlgoSel.algoList['values']
        if values == '':
            values  = []
        if isinstance(values, tuple):
            values  = list(values)
        values.append(node['name'])
        self.grpAlgoSel.algoList['values']  = values
        self.grpAlgoSel.algoList.current(len(values)-1)
        self.grpParams.appendAlgorithm(node)
        return node
        
    @property
    def currentAlgorithm(self):
        return self.algorithms[self.grpAlgoSel.algoList.get()]
            
    @Scripting.printable    
    def plotCurrentData(self):        
        self.figureBook.plot(self.currentData)