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


from wavesynlib.guicomponents.tk import Group, LabeledEntry
from wavesynlib.interfaces.windows.shell.constants import TBPFLAG
from wavesynlib.guicomponents.classselector import ask_class_name
from wavesynlib.application import Application
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.languagecenter.utils import auto_subs, eval_format, set_attributes, Nonblocking
from wavesynlib.languagecenter.wavesynscript import ScriptCode, Scripting
from wavesynlib.mathtools import Algorithm, AlgorithmDict, AlgorithmNode

import threading
import json


class OptimizeGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance    
        self.__topwin = kwargs.pop('topwin')

        super(OptimizeGroup, self).__init__(*args, **kwargs)
        
      
        
        parameter_frame    = Frame(self)
        parameter_frame.pack(side=LEFT, expand=YES, fill=Y)
        self.__num = LabeledEntry(parameter_frame)
        set_attributes(self.__num,
            label_text   = 'num',
            entry_text   = '1',
            label_width  = 5,
            entry_width  = 8,
            checker_function   = self._app.check_int
        )
        self.__num.entry.bind('<Return>', lambda event: self._on_solve_click())
        self.__num.pack(side=TOP)

     

        self.__pci  = LabeledEntry(parameter_frame)
        set_attributes(self.__pci,
            label_text   = 'PCI',
            entry_text   = '100',
            label_width  = 5,
            entry_width  = 8,
            checker_function   = self._app.check_int
        )
        self.__pci.pack(side=TOP)
        
        self.__parallel_checker_variable    = IntVar()
        self.__parallel_checker  = Checkbutton(parameter_frame, text="Parallel", variable=self.__parallel_checker_variable)
        self.__parallel_checker.pack()
        
        progfrm = Frame(self)
        progfrm.pack(side=LEFT, expand=YES, fill=Y)

        self.__genbtn = Button(progfrm, text='Generate', command=self._on_solve_click)
        self.__genbtn.pack(side=TOP)  
        Button(progfrm, text='Stop', command=self._on_stop_button_click).pack(side=TOP)         
        
        self.__progressbar_variable = IntVar()
        self.__finishedwav = IntVar()        
        self.__progressbar = Progressbar(progfrm, orient='horizontal', variable=self.__progressbar_variable, maximum=100)
        self.__progressbar.pack(side=LEFT)
        self.__progressbar.config(length=55)   
        self.__finishedwavbar = Progressbar(progfrm, orient='horizontal', variable=self.__finishedwav)
        self.__finishedwavbar.pack(side=LEFT)
        self.__finishedwavbar.config(length=30)  


        self.name = 'Generate'

        self.getparams = None
        self.__stopflag = False
        
    def _on_solve_click(self):
        t1  = time.clock()
        if self.__parallel_checker_variable.get():
            self.parallel_run()
        else:
            self.serial_run()        
        delta_t  = time.clock() - t1
        print(auto_subs('Total time consumption: $delta_t (s)'))

    def serial_run(self):
        app    = self._app
        taskbar_icon = app.taskbar_icon
        self.__stopflag = False
        wavnum = self.__num.get_int()
        progress = [0]
        waveform = [0]

        algorithm   = self.__topwin.current_algorithm          

        params = self.__topwin.parameter_group.get_parameters()

        if algorithm.need_cuda:
            class AlgoThread(object):
                def __init__(self, algo, params, waveform, progress):                    
                    app.cudaWorker.activate()
                    self.__params   = params,
                    self.__algo     = algo
                
                def start(self):
                    params  = self.__params[0]
                    for p in params:
                        if hasattr(params[p], 'code'): # Temp solution
                            params[p]   = eval(params[p].code)
                    app.cudaWorker.messageIn.put({'command':'call', 'callable object':self.__algo.run, 'args':[], 'kwargs':params})
                    
                def is_alive(self):
                    ret         = None
                    try:
                        ret     = app.cudaWorker.messageOut.get_nowait()
                    except:
                        pass
                    return False if ret else True
        else:
            class AlgoThread(threading.Thread):
                def __init__(self, algo, params, waveform, progress):
                    self.algo = algo
                    self.progress = progress
                    threading.Thread.__init__(self)
                def run(self):
                    printCode   = True
                    self.algo.run(**params)
        
        self.__finishedwavbar['maximum'] = wavnum

        def progress_checker(k, K, y, *args, **kwargs):                
            progress[0] = int(k / K * 100)                  
            
        algorithm.progress_checker.append(progress_checker)
        algorithm.progress_checker.interval  = int(self.__pci.entry_text)
        
        algorithm.presetParams(params) # for algorithms which will allocate resources depend on parameters and allocation procedure must be executed in the main thread.        
        
        try:
            for cnt in range(wavnum):
                algothread = AlgoThread(algorithm, params, waveform, progress)
                algothread.start()
    
                while algothread.is_alive():
                    self.__progressbar_variable.set(progress[0])
                    taskbar_icon.progress = int((cnt*100+progress[0])/(wavnum*100)*100)
                    self.__topwin.update()
                    if self.__stopflag:
                        break
                    time.sleep(0.05)
                self.__progressbar_variable.set(0)
                if self.__stopflag:
                    break
                printCode   = True
                self.__topwin.plot_current_data()
                self.__finishedwav.set(cnt+1)
        finally:
            algorithm.progress_checker.remove(progress_checker)
        self.__finishedwav.set(0)
        taskbar_icon.state = TBPFLAG.TBPF_NOPROGRESS
        
    def parallel_run(self):
        class AlgoThread(threading.Thread):
            def __init__(self, algorithm, parameters, num):
                self.algorithm  = algorithm
                self.parameters = parameters
                self.num        = num
                super(AlgoThread, self).__init__()
            def run(self):
                printCode   = True
                #parameters  = Scripting.convert_args_to_str(**self.parameters)
                paramStr    = eval_format('[([], dict({Scripting.convert_args_to_str(**self.parameters)}))]*{self.num}')
                self.algorithm.parallel_run_and_plot(ScriptCode(paramStr))
        algorithm   = self.__topwin.current_algorithm
        parameters  = self.__topwin.parameter_group.get_parameters()
        theThread   = AlgoThread(algorithm, parameters, self.__num.get_int())
        theThread.start()
        while theThread.is_alive():
            self.__topwin.update()            
            time.sleep(0.05)
            

    def _on_stop_button_click(self):
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

    def append_algorithm(self, algorithm):
        #To do: when algo is reset, the frm should be removed
        for algoName in self.__frameDict:
            self.__frameDict[algoName]['frame'].pack_forget()
        frm = Frame(self)
        frm.pack()
        paramInfo   = {}
        params = algorithm['parameters']
        for index, name in enumerate(params):
            param = params[name]
            paramitem = LabeledEntry(frm)
            paramitem.label_text = name
            paramitem.label_width = 5
            paramitem.entry_width = 8
            if self.balloon:
                self.balloon.bind_widget(paramitem.label, balloonmsg=param.shortdesc)
            if param.type == 'int':
                paramitem.checker_function = self._app.check_int
            elif param.type == 'float':
                paramitem.checker_function = self._app.check_float
            paramitem.grid(row=index%self.__MAXROW, column=index//self.__MAXROW)
            #self.__params[param.name] = {'gui':paramitem, 'meta':param}
            paramInfo[param.name] = {'gui':paramitem, 'meta':param}
        self.__algo = algorithm
        #self.__frameDict[algorithm.meta.name]   = frm
        self.__frameDict[algorithm['name']]   = dict(frame=frm, paramInfo=paramInfo)
        self.__params   = paramInfo

    def get_parameters(self):
        params = self.__params
        convert = {'int':int, 'float':float, 'expression':lambda expr: ScriptCode(expr), '':lambda x: x}
        return {name: convert[params[name]['meta'].type](params[name]['gui'].entry_text) for name in params}
        
    def change_algorithm(self, algorithmName):
        for algoName in self.__frameDict:
            self.__frameDict[algoName]['frame'].pack_forget()        
        self.__frameDict[algorithmName]['frame'].pack()
        self.__params   = self.__frameDict[algorithmName]['paramInfo']
        
        
class AlgoSelGroup(Group):
    def __init__(self, *args, **kwargs):
        self._topwin  = kwargs.pop('topwin')
        super(AlgoSelGroup, self).__init__(*args, **kwargs)
        
        self.__algorithm_list = Combobox(self, value=[], takefocus=1, stat='readonly', width=12)
        self.__algorithm_list['values']   = []
        self.__algorithm_list.pack()
        self.__algorithm_list.bind('<<ComboboxSelected>>', self._on_algorithm_change)
        
        Button(self, text='Load Algorithm', command=self._on_load_algorithm).pack()
        
        self.name = 'Algorithms'          
        
    @property
    def algorithm_list(self):
        return self.__algorithm_list
        
    def _on_algorithm_change(self, event):
        self._topwin.change_algorithm(event.widget.get())
        
    def _on_load_algorithm(self):
        printCode   = True
        
        funcObj    = Nonblocking(ask_class_name)('wavesynlib.algorithms', Algorithm)
        while funcObj.isRunning():
            Application.do_events()
            time.sleep(0.1)
        
        classInfo   = funcObj.return_value        
        
        if not classInfo:
            return
        module_name, class_name   = classInfo
        self._topwin.load_algorithm(module_name=module_name, class_name=class_name)


class SingleWindow(FigureWindow):      
    windowName  = 'WaveSyn-SingleSyn' 

    _xmlrpcexport_  = ['load_algorithm']
       
    def __init__(self, *args, **kwargs):     
        FigureWindow.__init__(self, *args, **kwargs)
        self.current_data    = None
                
        # algorithm dict and current data
        self.algorithms = AlgorithmDict()
        self.lock_attribute('algorithms')
        #        
        
        # The toolbar
        tool_tabs    = self.tool_tabs
        figure_book  = self.figure_book
        
        frmAlgo = Frame(tool_tabs)
        algorithm_selection_group  = AlgoSelGroup(frmAlgo, topwin=self)
        algorithm_selection_group.pack(side=LEFT, fill=Y)
        
        parameter_group   = ParamsGroup(frmAlgo, topwin=self)
        parameter_group.pack(side=LEFT, fill=Y)
        
        solve_group    = OptimizeGroup(frmAlgo, topwin=self)
        solve_group.pack(side=LEFT, fill=Y)
        tool_tabs.add(frmAlgo, text='Algorithm')
        
        with self.attribute_lock:
            set_attributes(self,
                algorithm_selection_group  = algorithm_selection_group,
                parameter_group   = parameter_group,
                solve_group    = solve_group                         
            )
        

        
        self.make_view_tab()
        self.make_marker_tab()
        self.make_export_tab()
        # End toolbar
        figure_book.make_figures(
            figure_meta  = [
                dict(name='Envelope',           polar=False),
                dict(name='Phase',              polar=False),
                dict(name='AutoCorrelation',    polar=False),
                dict(name='PSD',                polar=False)
            ]
        )
        
        with open(Application.instance.config_file_path) as f:
            config  = json.load(f)
        algorithms  = config['SingleWaveformAlgorithms']

        for algo in algorithms:
            self.load_algorithm(module_name=algo['ModuleName'], class_name=algo['ClassName'])

        self.algorithm_selection_group.algorithm_list.current(len(algorithms)-1)
        
        envelope_figure = figure_book[0]
        envelope_figure.plot_function  = lambda current_data, *args, **kwargs:\
            envelope_figure.plot(abs(current_data), *args, **kwargs)
        
        phase_figure    = figure_book[1]
        phase_figure.plot_function   = lambda current_data, *args, **kwargs:\
            phase_figure.plot(angle(current_data), *args, **kwargs)
            
        def plot_acdb(current_data, *args, **kwargs):
            s   = current_data
            if not isinstance(s, ndarray):
                s   = array(s)
            N       = len(s)
            ac      = convolve(s, conj(s[::-1]))
            acdb    = 20*log10(abs(ac))
            acdb    = acdb - max(acdb)
            autocorrelatino_figure.plot(r_[(-N+1):N], acdb, *args, **kwargs)            
            
        autocorrelatino_figure     = figure_book[2]
        autocorrelatino_figure.plot_function    = plot_acdb
            
        psd_figure      = figure_book[3]
        psd_figure.plot_function     = lambda current_data, *args, **kwargs:\
            psd_figure.plot(abs(fft.fft(current_data)), *args, **kwargs)
            
    
    @Scripting.printable        
    def load_algorithm(self, module_name, class_name):
        node    = AlgorithmNode(module_name, class_name)
        self.algorithms.add(node)
        values  = self.algorithm_selection_group.algorithm_list['values']
        if values == '':
            values  = []
        if isinstance(values, tuple):
            values  = list(values)
        values.append(node['name'])
        self.algorithm_selection_group.algorithm_list['values']  = values
        self.algorithm_selection_group.algorithm_list.current(len(values)-1)
        self.parameter_group.append_algorithm(node)

        
    def change_algorithm(self, algorithmName):
        self.parameter_group.change_algorithm(algorithmName)        
        
    @property
    def current_algorithm(self):
        return self.algorithms[self.algorithm_selection_group.algorithm_list.get()]
            
