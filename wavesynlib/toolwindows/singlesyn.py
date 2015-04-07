# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:45:33 2014

@author: Feng-cong Li
"""
from __future__ import print_function, division

from numpy import *
import time
from Tkinter import *
from ttk import *

from wavesynlib import guicomponents
from wavesynlib.guicomponents.tk  import Group, ParamItem
from wavesynlib.guicomponents.classselector import askClassName
from wavesynlib.application       import Application, ScriptCode, Scripting
from wavesynlib.basewindow        import FigureWindow
from wavesynlib.common            import setMultiAttr, autoSubs, evalFmt, Nonblocking
from wavesynlib.mathtools         import Algorithm, AlgorithmDict, AlgorithmNode


import threading
import json





class OptimizeGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance    
        self.__topwin = kwargs.pop('topwin')

        super(OptimizeGroup, self).__init__(*args, **kwargs)
        
      
        
        paramFrm    = Frame(self)
        paramFrm.pack(side=LEFT, expand=YES, fill=Y)
        self.__num = ParamItem(paramFrm)
        setMultiAttr(self.__num,
            labelText   = 'num',
            entryText   = '1',
            labelWidth  = 5,
            entryWidth  = 8,
            checkFunc   = self._app.checkInt
        )
        self.__num.entry.bind('<Return>', lambda event: self.onSolveClick())
        self.__num.pack(side=TOP)

     

        self.__pci  = ParamItem(paramFrm)
        setMultiAttr(self.__pci,
            labelText   = 'PCI',
            entryText   = '100',
            labelWidth  = 5,
            entryWidth  = 8,
            checkFunc   = self._app.checkInt
        )
        self.__pci.pack(side=TOP)
        
        self.__bParallel    = IntVar()
        self.__chkParallel  = Checkbutton(paramFrm, text="Parallel", variable=self.__bParallel)
        self.__chkParallel.pack()
        
        progfrm = Frame(self)
        progfrm.pack(side=LEFT, expand=YES, fill=Y)

        self.__genbtn = Button(progfrm, text='Generate', command=self.onSolveClick)
        self.__genbtn.pack(side=TOP)  
        Button(progfrm, text='Stop', command=self.onStopBtnClick).pack(side=TOP)         
        
        self.__progress = IntVar()
        self.__finishedwav = IntVar()        
        self.__progbar = Progressbar(progfrm, orient='horizontal', variable=self.__progress, maximum=100)
        self.__progbar.pack(side=LEFT)
        self.__progbar.config(length=55)   
        self.__finishedwavbar = Progressbar(progfrm, orient='horizontal', variable=self.__finishedwav)
        self.__finishedwavbar.pack(side=LEFT)
        self.__finishedwavbar.config(length=30)  


        self.name = 'Generate'

        self.getparams = None
        self.__stopflag = False
        
    def onSolveClick(self):
        t1  = time.clock()
        if self.__bParallel.get():
            self.parallelRun()
        else:
            self.serialRun()        
        deltaT  = time.clock() - t1
        print(autoSubs('Total time consumption: $deltaT (s)'))

    def serialRun(self):
        tbicon = self._app.tbicon
        self.__stopflag = False
        wavnum = self.__num.getInt()
        progress = [0]
        waveform = [0]

        algorithm   = self.__topwin.currentAlgorithm          

        params = self.__topwin.grpParams.getParams()

        class AlgoThread(threading.Thread):
            def __init__(self, algo, params, waveform, progress):
                self.algo = algo
                self.progress = progress
                threading.Thread.__init__(self)
            def run(self):
                printCode   = True
                self.algo.run(**params)
        
        self.__finishedwavbar['maximum'] = wavnum

        def progressChecker(k, K, y, *args, **kwargs):                
            progress[0] = int(k / K * 100)                  
            
        algorithm.progressChecker.append(progressChecker)
        algorithm.progressChecker.interval  = int(self.__pci.entryText)
        try:
            for cnt in range(wavnum):
                algothread = AlgoThread(algorithm, params, waveform, progress)
                algothread.start()
    
                while algothread.isAlive():
                    self.__progress.set(progress[0])
                    tbicon.progress = int((cnt*100+progress[0])/(wavnum*100)*100)
                    self.__topwin.update()
                    if self.__stopflag:
                        break
                    time.sleep(0.05)
                self.__progress.set(0)
                if self.__stopflag:
                    break
                printCode   = True
                self.__topwin.plotCurrentData()
                self.__finishedwav.set(cnt+1)
        finally:
            algorithm.progressChecker.remove(progressChecker)
        self.__finishedwav.set(0)
        tbicon.state = guicomponents.tk.TBPF_NOPROGRESS
        
    def parallelRun(self):
        class AlgoThread(threading.Thread):
            def __init__(self, algorithm, parameters, num):
                self.algorithm  = algorithm
                self.parameters = parameters
                self.num        = num
                super(AlgoThread, self).__init__()
            def run(self):
                printCode   = True
                #parameters  = Scripting.paramsToStr(**self.parameters)
                paramStr    = evalFmt('[([], dict({Scripting.paramsToStr(**self.parameters)}))]*{self.num}')
                self.algorithm.parallelRunAndPlot(ScriptCode(paramStr))
        algorithm   = self.__topwin.currentAlgorithm
        parameters  = self.__topwin.grpParams.getParams()
        theThread   = AlgoThread(algorithm, parameters, self.__num.getInt())
        theThread.start()
        while theThread.isAlive():
            self.__topwin.update()            
            time.sleep(0.05)
            

    def onStopBtnClick(self):
        self.__stopflag = True



class ParamsGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin   = kwargs.pop('topwin')
        self.balloon    = self._app.balloon

        #Group.__init__(self, *args, **kwargs)
        super(ParamsGroup, self).__init__(*args, **kwargs)
        self.__algo = None
        self.__MAXROW = 3
        self.__params = {}  

        self.__frameDict    = {}
          
        self.name = 'Parameters'

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
            paramitem.labelWidth = 5
            paramitem.entryWidth = 8
            if self.balloon:
                self.balloon.bind_widget(paramitem.label, balloonmsg=param.shortdesc)
            if param.type == 'int':
                paramitem.checkFunc = self._app.checkInt
            elif param.type == 'float':
                paramitem.checkFunc = self._app.checkFloat
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
        super(AlgoSelGroup, self).__init__(*args, **kwargs)
        
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
        self._topwin.changeAlgorithm(event.widget.get())
        
    def onLoadAlgorithm(self):
        printCode   = True
        
        funcObj    = Nonblocking(askClassName)('wavesynlib.algorithms', Algorithm)
        while funcObj.isRunning():
            self._topwin.update()
            time.sleep(0.1)
        classInfo   = funcObj.returnValue
        
        if not classInfo:
            return
        moduleName, className   = classInfo
        self._topwin.loadAlgorithm(moduleName=moduleName, className=className)


class SingleWindow(FigureWindow):      
    windowName  = 'WaveSyn-SingleSyn' 

    _xmlrpcexport_  = ['loadAlgorithm']
       
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
        self.makeMarkerTab()
        self.makeExportTab()
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

        self.grpAlgoSel.algoList.current(len(algorithms)-1)
        
        figEnvelope = figureBook[0]
        figEnvelope.plotFunction  = lambda currentData, *args, **kwargs:\
            figEnvelope.plot(abs(currentData), *args, **kwargs)
        
        figPhase    = figureBook[1]
        figPhase.plotFunction   = lambda currentData, *args, **kwargs:\
            figPhase.plot(angle(currentData), *args, **kwargs)
            
        def plot_acdb(currentData, *args, **kwargs):
            s   = currentData
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
        figPSD.plotFunction     = lambda currentData, *args, **kwargs:\
            figPSD.plot(abs(fft.fft(currentData)), *args, **kwargs)
            
    
    @Scripting.printable        
    def loadAlgorithm(self, moduleName, className):
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

        
    def changeAlgorithm(self, algorithmName):
        self.grpParams.changeAlgorithm(algorithmName)        
        
    @property
    def currentAlgorithm(self):
        return self.algorithms[self.grpAlgoSel.algoList.get()]
            